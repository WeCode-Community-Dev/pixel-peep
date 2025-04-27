from collections import defaultdict


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
    def add_node(self,n):
        self.graph[n]

    def add_edge(self, n, e):
        self.graph[n].append(e)

    def get_connected_components(self):
        visited=set()
        groups=[]
        def dfs(node,gr):
            if node in visited:
                return
            visited.add(node)
            gr.append(node)
            for nei in self.graph[node]:
                dfs(nei,gr)

        for node in self.graph:
            if node in visited:
                continue
            gr=[]
            dfs(node,gr)
            groups.append(gr)
        return groups