from pyopenie import OpenIE5
from typing import Any
import matplotlib.pyplot as plt
import networkx as nx


class RelationshipExtractor:
    def __init__(self, tokenized_sentences: str, chosen_chapter: int):
        # Initialize any necessary variables or models here
        self.extractor = OpenIE5('http://localhost:8000')
        self.extraced_relationships = self.extract_relationships(tokenized_sentences[chosen_chapter])
        print(self.extraced_relationships)
    
    def extract_relationships(self, sentences: list[str]) -> list[Any]:
        """Extract relationships from the given sentences."""
        relationships = []
        for sentence in sentences:
            relationships.append(self.extractor.extract(sentence))
        return relationships

class RelationshipParser:
    def __init__(self, sentence_relationships: list[Any]):
        # Initialize any necessary variables or models here
        self.sentence_relationships = sentence_relationships
        self.parsed_relationships = self.parse_relationships()
        self.plot_triplets(self.parsed_relationships[1:100])
    
    def parse_relationships(self) -> list[tuple[list[str], float]]:
        """Parse the relationships into a more structured format."""
        parsed_relationships = []
        for sentence_relationships in self.sentence_relationships:
            for relationship in sentence_relationships:
                if len(relationship) == 0:
                    continue
                extraction = relationship["extraction"]
                temp_list = []
                if "arg1" not in extraction:
                    continue
                temp_list.append(extraction["arg1"]["text"])
                if "rel" not in extraction:
                    continue
                temp_list.append(extraction["rel"]["text"])
                if "arg2s" in extraction:
                    for arg2 in extraction["arg2s"]:
                        temp_list.append(arg2["text"])
                parsed_relationships.append((temp_list, relationship["confidence"]))
        # Sort the parsed relationships by the confidence score in descending order
        parsed_relationships.sort(key=lambda x: x[1], reverse=True)
        return parsed_relationships
    
    def plot_triplets(self, parsed_relationships: list[tuple[list[str], float]]):
        """Plot the extracted relationships."""
        G = nx.DiGraph()
        for relationship in parsed_relationships:
            entities = relationship[0]
            subject = entities[0]
            relation = entities[1]
            for obj in entities[2:]:
                print(subject)
                G.add_edge(subject, obj, relationship=relation)
        pos = nx.spring_layout(G)

        nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue')

        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, edge_color='g')

        edge_labels = nx.get_edge_attributes(G, 'relationship')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

        plt.title("Unprioritized Relationships")
        plt.axis('off')
        plt.show()
        plt.savefig('Assets/KnowledgeGraphs/unprioritised_relationships.png')