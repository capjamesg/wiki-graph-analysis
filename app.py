import os
import re

import networkx as nx
import matplotlib.pyplot as plt

WIKI_DIR = "./breakfastand.coffee/data/"

# walk through the directory

definitions = {}

links = {}

def link_refactor(text):
    # return [[text]] -> text

    return re.findall(r"\[\[(.*?)\]\]", text)

for root, dirs, files in os.walk(WIKI_DIR):
    for file in files:
        if file.endswith(".txt"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                content = f.read()

                # find line with <dfn>
                for line in content.split("\n"):
                    if "<dfn>" in line:
                        # extract definition
                        term = file.replace(".txt", "")
                        definition = line.replace("<dfn>", "").replace("</dfn>", "")
                        definitions[term] = definition
                    
                        break

for d in definitions:
    links[d] = []

    found_links_in_definition = link_refactor(definitions[d])

    for l in found_links_in_definition:
        if "|" in l:
            l = l.split("|")[0]

        l = l.replace("_", " ")

        links[d].append(l)
        
# create graph
G = nx.DiGraph()

for d in definitions:
    G.add_node(d)

    for l in links[d]:
        G.add_edge(d, l)

# draw graph
nx.draw(G, with_labels=True, font_weight='bold')

# plt.show()

# dump as json
import json

with open("graph.json", "w") as f:
    json.dump(nx.node_link_data(G), f)