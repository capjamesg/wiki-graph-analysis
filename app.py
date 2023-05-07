import json
import os
import re
from urllib.parse import unquote

import matplotlib.pyplot as plt
import networkx as nx

WIKI_DIR = "./wiki/data/"


def link_refactor(text):
    return re.findall(r"\[\[(.*?)\]\]", text)


def get_definitions() -> dict:
    """
    Get all definitions from the wiki

    :return: dict of definitions
    :rtype: dict
    """
    definitions = {}

    for root, _, files in os.walk(WIKI_DIR):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    content = f.read()

                    # find line with <dfn>
                    for line in content.split("\n"):
                        if "<dfn>" in line or "<b>" in line:
                            # extract definition
                            term = file.replace(".txt", "")
                            definition = line.replace("<dfn>", "").replace("</dfn>", "")
                            definitions[term.lower()] = definition

                            break

    return definitions


def create_link_graph(definitions) -> dict:
    links = {}

    found_links = 0

    for d in definitions:
        d = d.lower()

        links[d] = []

        found_links_in_definition = link_refactor(definitions[d])

        found_links_in_definition = [l.lower() for l in found_links_in_definition]

        for l in found_links_in_definition:
            if "|" in l:
                l = l.split("|")[0]

            l = l.replace("_", " ")

            links[l] = links.get(l, []) + [d]

            found_links += 1

    return links, found_links


def create_graphviz_graph(definitions, links) -> dict:
    visualizations = {}

    for d in definitions:
        G = nx.DiGraph()

        # decode url
        term = unquote(d).lower()

        if links.get(term) is None:
            continue

        G.add_node(term)

        for l in links[term]:
            print(l)
            G.add_node(l)
            G.add_edge(term, l)

            for l2 in links.get(l, []):
                G.add_node(l2)
                G.add_edge(l, l2)

                for l3 in links.get(l2, []):
                    G.add_node(l3)
                    G.add_edge(l2, l3)

        graphviz_graph = nx.nx_agraph.to_agraph(G)

        # left to right instead of top to bottom
        graphviz_graph.graph_attr.update(rankdir="LR")

        visualizations[d] = graphviz_graph.to_string()

    with open("graph.json", "w") as f:
        json.dump(nx.node_link_data(G), f)

    return visualizations


def main():
    definitions = get_definitions()

    links, found_links = create_link_graph(definitions)

    print("Found links:", found_links)

    visualizations = create_graphviz_graph(definitions, links)

    with open("visualizations.json", "w") as f:
        json.dump(visualizations, f)

if __name__ == "__main__":
    main()