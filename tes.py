import networkx as nx
import matplotlib.pyplot as plt

# Membuat graph baru
G = nx.Graph()

# Menambahkan edge atau hubungan antara simpul (nodes)
G.add_edge('A', 'B')
G.add_edge('B', 'C')
G.add_edge('C', 'D')
G.add_edge('D', 'A')

# Menampilkan graph
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_color='black')
plt.show()