from pyopenie import OpenIE5
from typing import Any
from artificer.preprocessor.core import Preprocessor
import matplotlib.pyplot as plt
import networkx as nx
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn
import numpy as np

class Relationship:
    def __init__(self, 
                 subject: str,
                 processed_subject: list[str],
                 processed_subject_props: dict[str, list[float]],
                 relation: str, 
                 object: str, 
                 processed_object: str, 
                 processed_object_props: dict[str, list[float]],
                 confidence: float, 
                 original_sentence: str):
        self.subject = subject
        self.processed_subject = processed_subject
        self.processed_subject_props = processed_subject_props
        self.relation = relation
        self.object = object
        self.processed_object = processed_object
        self.processed_object_props = processed_object_props
        self.confidence = confidence
        self.original_sentence = original_sentence
    
    def __repr__(self):
        return (
            f"Subject: {self.subject}, \n"
            f"Processed Subject: {self.processed_subject}, \n"
            f"Processed Subject Props: {self.processed_subject_props}, \n"
            f"Relation: {self.relation}, \n"
            f"Object: {self.object}, \n"
            f"Processed Object: {self.processed_object}, \n"
            f"Processed Object Props: {self.processed_object_props}, \n"
            f"Confidence: {self.confidence}, \n"
            f"Original Sentence: {self.original_sentence}\n"
        )


class RelationshipSerialiser:

    def toDict(relationship: Relationship) -> dict:
        return {
            "subject": relationship.subject,
            "processed_subject": relationship.processed_subject,
            "processed_subject_props": relationship.processed_subject_props,
            "relation": relationship.relation,
            "object": relationship.object,
            "processed_object": relationship.processed_object,
            "processed_object_props": relationship.processed_object_props,
            "confidence": relationship.confidence,
            "original_sentence": relationship.original_sentence
        }
    
    def fromDict(relationship_dict: dict) -> Relationship:
        return Relationship(
            subject=relationship_dict["subject"],
            processed_subject=relationship_dict["processed_subject"],
            processed_subject_props=relationship_dict["processed_subject_props"],
            relation=relationship_dict["relation"],
            object=relationship_dict["object"],
            processed_object=relationship_dict["processed_object"],
            processed_object_props=relationship_dict["processed_object_props"],
            confidence=relationship_dict["confidence"],
            original_sentence=relationship_dict["original_sentence"]
        )


class RelationshipExtractor:
    def __init__(self, tokenized_sentences: str, chosen_chapter: int):
        # Initialize any necessary variables or models here
        self.extractor = OpenIE5('http://localhost:8000')
        self.extracted_relationships = self.extract_relationships(tokenized_sentences[chosen_chapter])
        # print(self.extracted_relationships)
    
    def extract_relationships(self, sentences: list[str]) -> list[Any]:
        """Extract relationships from the given sentences."""
        relationships = []
        for sentence in sentences:
            relationships.append(self.extractor.extract(sentence))
        return relationships

class RelationshipParser:
    def __init__(self, sentence_relationships: list[Any], 
                 preprocesser: Preprocessor, 
                 key_nouns: dict[str, float], 
                 phrase_length_limit: int, 
                 key_phrase_metric_tresh: float):
        # Initialize any necessary variables or models here
        self.sentence_relationships = sentence_relationships
        self.key_nouns = key_nouns
        self.phrase_length_limit = phrase_length_limit
        self.key_phrase_metric_tresh = key_phrase_metric_tresh
        self.phrase_count_dict = {}
        self.wordnet_depth_memo = {}
        self.processed_relationships = []
        self.preprocessor = preprocesser
        self.process_relationships()
        self.filtered_relationships: list[Relationship] = self.filter_relationships()

        # print(self.filtered_relationships)
        # print(len(self.filtered_relationships))
        self.plot_triplets(self.filtered_relationships)
    
    def export_key_phrases(self, export_path: str):
        """Export the key phrases to a text file."""
        key_phrases = set()
        for relationship in self.filtered_relationships:
            key_phrases.add(relationship.subject)
            key_phrases.add(relationship.object)

        with open(export_path, 'w') as file:
            for phrase in key_phrases:
                file.write(f"{phrase}\n")
    
    def process_relationships(self):
        """Process the relationships from the OpenIE output into nice Relationship objects."""
        for sentence_data in self.sentence_relationships:
            sentence_key_phrases = set()
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
                new_subject = " ".join(processed_subject)
                if new_subject not in sentence_key_phrases:
                    sentence_key_phrases.add(new_subject)


                arg2s = extraction["arg2s"]
                for arg2 in arg2s:
                    arg2_text = arg2["text"]
                    processed_object = self.process_phrase(arg2_text)
                    if not processed_object or len(processed_object) == 0:
                        # Skip the relationship if the object is empty
                        continue
                    new_object = " ".join(processed_object)
                    if new_object not in sentence_key_phrases:
                        sentence_key_phrases.add(new_object)
                    self.processed_relationships.append(
                        Relationship(
                            subject=new_subject,
                            processed_subject=processed_subject,
                            processed_subject_props = self.get_phrase_props(processed_subject, original_sentence ),
                            relation=extraction["rel"]["text"],
                            object=new_object,
                            processed_object=processed_object,
                            processed_object_props = self.get_phrase_props(processed_object, original_sentence),
                            confidence=relationship["confidence"],
                            original_sentence=original_sentence
                        )
                    )
            for phrase in sentence_key_phrases:
                if phrase in self.phrase_count_dict:
                    self.phrase_count_dict[phrase] += 1
                else:
                    self.phrase_count_dict[phrase] = 1
        max_depth = max(self.wordnet_depth_memo.values())
        max_count = max(self.phrase_count_dict.values())
        for phrase in self.phrase_count_dict:
            self.phrase_count_dict[phrase] /= max_count
        for relationship in self.processed_relationships:
            for i in range(len(relationship.processed_subject)):
                relationship.processed_subject_props["wordnet_depths"][i] /= max_depth
            for i in range(len(relationship.processed_object)):
                relationship.processed_object_props["wordnet_depths"][i] /= max_depth
            relationship.processed_subject_props["count"] = self.phrase_count_dict[relationship.subject]
            relationship.processed_object_props["count"] = self.phrase_count_dict[relationship.object]
            relationship.processed_subject_props["key_phrase_metric"] = \
            np.average(relationship.processed_subject_props["tf_idf"]) + relationship.processed_subject_props["count"] \
            + np.average(relationship.processed_subject_props["wordnet_depths"])
            relationship.processed_object_props["key_phrase_metric"] = \
            np.average(relationship.processed_object_props["tf_idf"]) + relationship.processed_object_props["count"] \
            + np.average(relationship.processed_object_props["wordnet_depths"])
    
    def filter_relationships(self) -> list[Relationship]:
        """Filter the relationships based on the key phrase metric."""
        filtered_relationships = []
        for relationship in self.processed_relationships:
            if (relationship.processed_subject_props["key_phrase_metric"] > self.key_phrase_metric_tresh and 
                relationship.processed_object_props["key_phrase_metric"] > self.key_phrase_metric_tresh):
                filtered_relationships.append(relationship)
        return filtered_relationships
    
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
        return preprocessed_text
    
    def get_phrase_props(self, phrase: list[str], original_sentence: str) -> dict[str, list[float]]:
        """
        Get the properties of a phrase.
        Will give tf-idf and wordnet depth (unnormalised yet) here
        but will add the count later
        """
        tf_idf = [self.key_nouns[word] for word in phrase]
        wordnet_depths = self.get_wordnet_depths(phrase, original_sentence) 
        return {"tf_idf": tf_idf, "wordnet_depths": wordnet_depths}

    def get_wordnet_depths(self, phrase: list[str], original_sentence: str) -> list[float]:
        depths = []
        for i in range(len(phrase)):
            if phrase[i] in self.wordnet_depth_memo:
                depths.append(self.wordnet_depth_memo[phrase[i]])
                continue
            synset = lesk(original_sentence, phrase[i])
            if synset:
                self.wordnet_depth_memo[phrase[i]] = synset.min_depth()
                depths.append(synset.min_depth())
            else:
                print(f"Could not find synset for {phrase[i]}")
                more_synsets = wn.synsets(phrase[i])
                if len(more_synsets) == 0:
                    "Might need to give an average depth score instead of 0"
                    print(f"Could not find more synsets for {phrase[i]}")
                    self.wordnet_depth_memo[phrase[i]] = 0
                    depths.append(0)
                    continue

                max_depth = 0
                for candidate_synset in more_synsets:
                    for possible_synset in more_synsets:
                        similarity = candidate_synset.path_similarity(possible_synset)
                        if similarity:
                            # Track the synset with the maximum depth
                            print(f"Found backup similarity: {similarity}")
                            max_depth = max(max_depth, candidate_synset.min_depth())
                
                # Fallback: if no similarity found, use the depth of the most common synset
                if max_depth == 0:
                    most_common_synset = more_synsets[0]  # First synset is typically the most common
                    max_depth = most_common_synset.min_depth()
                self.wordnet_depth_memo[phrase[i]] = max_depth
                depths.append(max_depth)
        return depths
    
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

        plt.title("Key Relationships")
        plt.axis('off')
        plt.show()
        plt.savefig('Assets/KnowledgeGraphs/key_relationships.png')