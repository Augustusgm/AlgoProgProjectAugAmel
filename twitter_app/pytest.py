import networkx as nx

g = nx.DiGraph()

g.add_edge(1,2)
print(g.edges)
g.remove_edge(1,2)
print(g.edges)