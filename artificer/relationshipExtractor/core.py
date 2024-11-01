from pyopenie import OpenIE5
from typing import Any
from artificer.preprocessor.core import Preprocessor
import matplotlib.pyplot as plt
import networkx as nx

class Relationship:
    def __init__(self, 
                 subject: str,
                 processed_subject: list[str],
                 relation: str, 
                 object: str, 
                 processed_object: str, 
                 confidence: float, 
                 original_sentence: str):
        self.subject = subject
        self.processed_subject = processed_subject
        self.relation = relation
        self.object = object
        self.processed_object = processed_object
        self.confidence = confidence
        self.original_sentence = original_sentence
    
    def __repr__(self):
        return (
            f"Subject: {self.subject}, \n"
            f"Processed Subject: {self.processed_subject}, \n"
            f"Relation: {self.relation}, \n"
            f"Object: {self.object}, \n"
            f"Processed Object: {self.processed_object}, \n"
            f"Confidence: {self.confidence}, \n"
            f"Original Sentence: {self.original_sentence}\n"
        )


class RelationshipSerialiser:

    def toDict(relationship: Relationship) -> dict:
        return {
            "subject": relationship.subject,
            "processed_subject": relationship.processed_subject,
            "relation": relationship.relation,
            "object": relationship.object,
            "processed_object": relationship.processed_object,
            "confidence": relationship.confidence,
            "original_sentence": relationship.original_sentence
        }
    
    def fromDict(relationship_dict: dict) -> Relationship:
        return Relationship(
            subject=relationship_dict["subject"],
            processed_subject=relationship_dict["processed_subject"],
            relation=relationship_dict["relation"],
            object=relationship_dict["object"],
            processed_object=relationship_dict["processed_object"],
            confidence=relationship_dict["confidence"],
            original_sentence=relationship_dict["original_sentence"]
        )


class RelationshipExtractor:
    def __init__(self, tokenized_sentences: str, chosen_chapter: int):
        # Initialize any necessary variables or models here
        self.extractor = OpenIE5('http://localhost:8000')
        self.extracted_relationships = self.extract_relationships(tokenized_sentences[chosen_chapter])
        print(self.extracted_relationships)
    
    def extract_relationships(self, sentences: list[str]) -> list[Any]:
        """Extract relationships from the given sentences."""
        relationships = []
        for sentence in sentences:
            relationships.append(self.extractor.extract(sentence))
        return relationships

class RelationshipParser:
    def __init__(self, sentence_relationships: list[Any], preprocesser: Preprocessor, key_nouns: dict[str, float], phrase_length_limit: int):
        # Initialize any necessary variables or models here
        self.sentence_relationships = sentence_relationships
        self.key_nouns = key_nouns
        self.phrase_length_limit = phrase_length_limit
        # self.parsed_relationships = self.parse_relationships()
        self.processed_relationships = []
        self.preprocessor = preprocesser
        self.process_relationships()
        print(self.processed_relationships)
        # self.plot_triplets(self.parsed_relationships[1:100])
    
    def process_relationships(self):
        """Process the relationships from the OpenIE output into nice Relationship objects."""
        for sentence_data in self.sentence_relationships:
            for relationship in sentence_data:
                extraction = relationship["extraction"]
                original_sentence=relationship["sentence"]
                if "arg1" not in extraction:
                    continue
                if "arg2s" not in extraction:
                    continue
                arg1_text = extraction["arg1"]["text"]
                processed_subject = self.process_phrase(arg1_text)
                if not processed_subject or len(processed_subject) == 0:
                    # Skip the relationship if the subject is empty
                    continue
                arg2s = extraction["arg2s"]
                for arg2 in arg2s:
                    arg2_text = arg2["text"]
                    processed_object = self.process_phrase(arg2_text)
                    if not processed_object or len(processed_object) == 0:
                        # Skip the relationship if the object is empty
                        continue
                    self.processed_relationships.append(
                        Relationship(
                            subject=arg1_text,
                            processed_subject=processed_subject,
                            processed_subject_props = self.get_phrase_props(processed_subject, original_sentence ),
                            relation=extraction["rel"]["text"],
                            object=arg2_text,
                            processed_object=processed_object,
                            processed_object_props = self.get_phrase_props(processed_object, original_sentence),
                            confidence=relationship["confidence"],
                            original_sentence=original_sentence
                        )
                    )
    
    def process_phrase(self, text: str) -> list[str]:
        """Process a phrase via the preprocessing rules and limit the phrase length via the tfidfs."""
        preprocessed_text = self.preprocessor.process_phrase(text)
        # Filter out any words that are not key nouns
        preprocessed_text = [word for word in preprocessed_text if word in self.key_nouns]
        # Remove duplicates while preserving order
        seen = set()
        preprocessed_text = [x for x in preprocessed_text if not (x in seen or seen.add(x))]
        if len(preprocessed_text) > self.phrase_length_limit:
            print(f"Phrase too long: {preprocessed_text}")
            tf_idf_list = [self.key_nouns[word] for word in preprocessed_text]
            # Get the indices of the phrase_length_limit largest values in the tf_idf_list
            largest_indices = sorted(range(len(tf_idf_list)), key=lambda i: tf_idf_list[i], reverse=True)[:self.phrase_length_limit]
            largest_indices.sort()
            # Use those indices to access the words in the preprocessed_text to form another list
            preprocessed_text = [preprocessed_text[i] for i in largest_indices]
            print(f"Shortened phrase: {preprocessed_text}")
            return preprocessed_text
    
    def get_phrase_props(self, phrase: list[str], original_sentence: str) -> dict[str, list[float]]:
        """Get the properties of a phrase. will give tf-idf and wordnet depth here but will add the the count later"""
        tf_idf = [self.key_nouns[word] for word in phrase]
        wordnet_depths = self.get_wordnet_depths(phrase, original_sentence)
        return {"tf_idf": tf_idf}

    def get_wordnet_depths(self, phrase: list[str], original_sentence: str) -> list[float]:
        return [0.0] * len(phrase) # placeholder


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
    
    def plot_triplets(self, processed_relationships: list[Relationship]):
        """Plot the extracted relationships."""
        G = nx.DiGraph()
        for rel in processed_relationships:
            G.add_edge(rel.subject, rel.object, relationship = rel.relation)
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