import sys
import math
from common import print_tour, read_input
# heapの中身は辺の重みにより、昇順にソートされている
from heapq import heappush, heappop

def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


# ①初期経路を作成
#   2近似解法を採用(プリム法)
#       →c近似解法とは、最悪でもc倍の近似解が得られるアルゴリズムのこと
#   手順）   1, 最小全域木Tを求める
#               ここで以下のプリム法を使う
#               1, 都市を頂点とし、辺を一本も含まないグラフTを用意する
#               2, スタート点を一つ決める
#               3, 追加できる辺がなくなるまで以下を繰り返す
#                   ・スタート点から辿れる辺の中で最も重みが小さい辺をTに追加する
#                    注意：つながっているすべての点から辿れる辺かつ追加しても閉路にならないような辺であることが条件
#               4, 最終的に出来上がったTが最小全域木である
#           2, Tの枝を複製したグラフを作り、一筆書きで一周する
#               オイラー路（何回でも同じ辺、頂点を通って良い）を作る
#           3, すでに訪れた都市は再度訪れないようにし、全都市をちょうど一回ずつ通る閉路を作る
#               Hierholzer's Algorithm
#               →・ある点から始めてまたその点に戻るパスを見つけて（閉路）、通ったパスを除去
#                ・上記を繰り返してできた複数の閉路を繋ぎ合わせる
# ②経路を最適化
#   2-opt法を採用
#
# その他の解法：
#   プリム法 - クラスカル法
#   Hierholzer's Algorithm - Fleury's Algorithm


# プリム法で最小全域木を求める
def prim(cities):
    edge = []               #最小全域木に必要なへ辺(辺の重み、端点１、端点２)のリスト
    num_v = len(cities)     #頂点の数

    # 完全グラフの辺の情報をgraphで管理
    graph = [[] for _ in range(num_v)] 
    for v in range(num_v):
        for w in range(v+1, num_v):
            dist = distance(cities[v], cities[w])
            graph[v].append((w, dist))
            graph[w].append((v, dist))

    marked = [False for _ in range(num_v)]  #頂点をすでに通ったか確認するリスト
    marked_cnt = 0                          #すでに通った頂点数（ループの終了条件に利用）
    marked[0] = True
    marked_cnt += 1

    q = []   # heap q =  (weight, neighbor_v, me_v)を要素にもつ
    #　頂点graph[0]に隣接する辺をheapに保存
    for neighbor, weight in graph[0]:
        heappush(q, (weight, neighbor, 0))

    # 全ての頂点がマークされるまでループ
    while marked_cnt < num_v:
        # 最小の重みの辺をheapで取り出す
        weight, v, me = heappop(q)
        # マークされているならスキップ
        if marked[v]:
            continue
        # 頂点vをマークし、vに隣接する辺の情報を保存
        marked[v] = True
        marked_cnt += 1
        edge.append((weight, v, me))
        for w, weight in graph[v]:
            if marked[w]:
                continue
            heappush(q, (weight, w, v))
    
    return edge

# オイラーグラフから、一筆書きの経路を求める
def create_eulerian_path(edges):
    graph = {i:[] for i in range(len(edges) * 2)}
    # 逆方向の辺も追加して、オイラーグラフにする
    for _, v, w in edges:
        graph[v].append(w)
        graph[w].append(v)  #逆方向も追加してオイラーグラフにする

    # 閉路の構築
    path = []
    stack = [0]  # 始点をスタックに追加
    while stack:
        current = stack[-1] # stackに最後に追加された要素を参照
        if not graph[current]:
            path.append(stack.pop())
        else:
            next_vertex = graph[current].pop()
            stack.append(next_vertex)

    # スタート地点に戻るように閉路を調整
    path.reverse()
    path.append(path[0])

    return path

# オイラー路からハミルトン閉路を生成する
# Hierholzer's Algorithm
def create_hamiltonian_path(path):
    tour = []
    #　すでにたどった頂点を記録
    exist_vertex = set()
    # オイラー路を辿り、一度訪れたことのある頂点は飛ばす
    for vartex in path:
        if vartex not in exist_vertex:
            tour.append(vartex)
            exist_vertex.add(vartex)
    tour.append(0)
    return tour

def two_opt(tour, cities):
    N = len(tour)
    improved = True

    while improved:
        improved = False
        for i in range(1, N - 1):
            for j in range(i + 1, N):
                if j - i == 1: continue  # 隣接ノード間だけでは経路の改善ができないのでスキップ
                # 4点に関して辺を組み替えた方が短ければ
                if distance(cities[tour[i-1]], cities[tour[i]]) + distance(cities[tour[j-1]], cities[tour[j]]) \
                    > distance(cities[tour[i-1]], cities[tour[j-1]]) + distance(cities[tour[i]], cities[tour[j]]):
                    tour[i:j] = reversed(tour[i:j])
                    improved = True
    return tour


def solve():
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    # ① 初期経路を作成
    edges = prim(cities)
    eularian_path = create_eulerian_path(edges)
    hamiltonian_path = create_hamiltonian_path(eularian_path)
    tour = two_opt(hamiltonian_path, cities)

    # ②　経路を最適化

    # 経路の総コストを計算
    total = calculate_total_distance(tour, cities)
    return tour, total

def calculate_total_distance(tour, cities):
    N = len(tour)
    return sum(distance(cities[tour[i]], cities[tour[i+1]]) for i in range(N-1))

if __name__ == '__main__':
    tour, total_distance = solve()
    print('Tour:')
    print(tour)
    print('Total distance:')
    print(total_distance)