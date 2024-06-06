import sys
from collections import deque

class Wikipedia:

    # Initialize the graph of pages.
    def __init__(self, pages_file, links_file):

        # A mapping from a page ID (integer) to the page title.
        # For example, self.titles[1234] returns the title of the page whose
        # ID is 1234.
        # wiki.titles = { 1: 'title1', 2: 'title2', 3: 'title3', ...}
        self.titles = {}

        # A set of page links.
        # For example, self.links[1234] returns an array of page IDs linked
        # from the page whose ID is 1234.
        # wiki.links = { 1: [dst1, dst2, dst3], 2: [dst2, dst4], 3: [], ...}
        self.links = {}

        # Read the pages file into self.titles.
        with open(pages_file) as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert not id in self.titles, id
                self.titles[id] = title
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # Read the links file into self.links.
        with open(links_file) as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.titles, src
                assert dst in self.titles, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()

    # Find the longest titles. This is not related to a graph algorithm at all
    # though :)
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                count += 1
            index += 1
        print()


    # Find the most linked pages.
    def find_most_linked_pages(self):
        link_count = {}
        for id in self.titles.keys():
            link_count[id] = 0

        for id in self.titles.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked pages are:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.titles[dst], link_count_max)
        print()


    def get_key_by_value(self, value):
        for k, v in self.titles.items():
            if v == value:
                return k
        return None
    
    # Construct and return the shortest path from the start page to the goal page.
    # |goal_id| (int): The ID of the goal page.
    # |visited| (dict): A table representing the visited pages during BFS traversal.
    # Returns:
    #    list: A list representing the shortest path from the start page to the goal page.
    def follow_path(self, start_id, goal_id, visited):
        path = []
        current_id = goal_id
        while current_id != start_id:
            path.insert(0, self.titles[current_id])
            current_id = visited[current_id]
        path.insert(0, self.titles[start_id])
        return path
    
    # Find the shortest path.
    # |start|: The title of the start page.
    # |goal|: The title of the goal page.
    # Based on BFS.
    def find_shortest_path(self, start, goal):
        start_id = self.get_key_by_value(start)
        goal_id = self.get_key_by_value(goal)
        que = deque()
        visited = {start_id: None}  # startからの最短距離を格納
        que.append(start_id)
        while que:
            node = que.popleft()
            if node is None or goal_id is None:
                break
            elif node == goal_id:
                print(f"The shortest path from {start} to {goal} is: ")
                path = self.follow_path(start_id, goal_id, visited)
                print(path)
                print()
                return True
            else:
                for neighbor_id in self.links[node]:
                    if neighbor_id not in visited:
                        visited[neighbor_id] = node     # link: node -> neighbor 
                        que.append(neighbor_id)
        print(f"There is no path from {start} to {goal}.")
        print()
        return False


    # Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        length = len(self.titles)
        # current_rank_list = [] リストにすると早い。dictの場合はメモリを使う→キャッシュに入らないので遅くなる
        # updates_rank_listもリストにする
        current_rank_list = {id: 1.0 for id in self.titles.keys()}
        previous_updates = 0
        threshold = 0.01
        while True:
            updated_rank_list = {id: 0 for id in self.titles.keys()}
            updates = 0
            for id, rank in current_rank_list.items():
                # self.linksをlistでなくsetにするとデータが大きくなった時に早くなるよ
                if id not in self.links:
                    updates += rank / length
                    print("not in self.titles: ", updates)
                else:
                    for neighbor_id in self.links[id]:
                        updated_rank_list[neighbor_id] +=  0.85 * rank / len(self.links[id])
                    updates += 0.15 * rank / length
            if updates < threshold or (updates - previous_updates) < threshold:
                break
            else:
                for i in self.titles.keys():
                    updated_rank_list[i] += updates
            current_rank_list = updated_rank_list.copy()
            previous_updates = updates

        print("The most popular page is: ")
        highest_score_id = max(current_rank_list, key = current_rank_list.get)
        print(self.titles[highest_score_id])
        print()
    
    # Insert id in table, then sort the table.
    # Used in find_isolated_pages
    def insert_and_sort(self, targes_id, table):
        lo = 0
        hi = len(table) - 1
        while lo <= hi:
            m = (lo + hi) //2   # //は、割り算の結果を切り捨てて整数値とする
            if targes_id < table[m]:
                hi = m - 1
            elif targes_id > table[m]:
                lo = m + 1
            else: # When the target is found
                return (True, table)        
        table.insert(lo, targes_id)
        return (False, table)
    
    # Find isolated pages.
    def find_isolated_pages(self):
        connected_pages_id = []
        for id, dst in self.links.items():
            for i in dst:
                r  = self.insert_and_sort(i, connected_pages_id)
                connected_pages_id = r[1]
            r = self.insert_and_sort(id, connected_pages_id)
            connected_pages_id = r[1]
            print(id)
        
        isolated_pages = []
        for id in self.titles.keys():
            r = self.insert_and_sort(id, connected_pages_id)
            if not r[0]:
                isolated_pages.append(self.titles[id])
        
        if not isolated_pages:
            print("There are no isolated pages")
        else:
            print("The isolated pages are ", isolated_pages)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    wikipedia.find_longest_titles()
    wikipedia.find_most_linked_pages()
    wikipedia.find_shortest_path("A", "C")
    wikipedia.find_shortest_path("A", "E")
    wikipedia.find_shortest_path("E", "A")
    wikipedia.find_shortest_path("A", "A")
    wikipedia.find_shortest_path("渋谷", "パレートの法則")
    wikipedia.find_most_popular_pages()
    wikipedia.find_isolated_pages()
