from pyopenie import OpenIE5
from typing import Any
from dynamo.preprocessor.core import Preprocessor
import matplotlib.pyplot as plt
import networkx as nx
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn
import numpy as np
from dynamo.relationshipExtractor.types import Relationship, RelationshipType
from dynamo.sysMLAugmenter.types import BDDAttribute
from dynamo.attributeExtractor.core import AttributeExtractor

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
            "original_sentence": relationship.original_sentence,
        }
    
    def fromDict(relationship_dict: dict) -> Relationship:
        return Relationship(**relationship_dict)


class RelationshipExtractor:
    def __init__(self, tokenized_sentences: str, chosen_chapter: int):
        # Initialize any necessary variables or models here
        self.extractor = OpenIE5('http://localhost:8000')
        self.extracted_relationships = self.extract_relationships(tokenized_sentences[chosen_chapter])
    
    def extract_relationships(self, sentences: list[str]) -> list[Any]:
        """Extract relationships from the given sentences."""
        relationships = []
        for sentence in sentences:
            try:
                relationships.append(self.extractor.extract(sentence))
            except:
                print(f"Failed to extract relationships from sentence: {sentence}")
        return relationships

class RelationshipParser:
    def __init__(self, sentence_relationships: list[Any], 
                 preprocesser: Preprocessor, 
                 key_nouns: dict[str, float], 
                 phrase_length_limit: int, 
                 key_phrase_metric_tresh: float,
                 relationship_confidence_tresh: float = 0.5,
                 should_extract_attributes=True):
        # Initialize any necessary variables or models here
        self.sentence_relationships = sentence_relationships
        self.key_nouns = key_nouns
        self.phrase_length_limit = phrase_length_limit
        self.key_phrase_metric_tresh = key_phrase_metric_tresh
        self.relationship_confidence_tresh = relationship_confidence_tresh
        self.phrase_count_dict = {}
        self.wordnet_depth_memo = {}
        self.processed_relationships = []
        self.preprocessor = preprocesser
        self.bdd_attributes : list[BDDAttribute] = []
        self.should_extract_attributes = should_extract_attributes

        if should_extract_attributes:
            self.attribute_extractor: AttributeExtractor = AttributeExtractor()

        self.process_relationships()
        self.filtered_relationships: list[Relationship] = self.filter_relationships()
        self.key_phrases = self.get_key_phrases()
        self.bdd_attributes = self.filter_bdd_attributes()
        
        
    
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
                processed_subject = self.process_phrase_as_noun(arg1_text)
                if not processed_subject or len(processed_subject) == 0:
                    # Skip the relationship if the subject is empty
                    continue
                new_subject = " ".join(processed_subject)
                if new_subject not in sentence_key_phrases:
                    sentence_key_phrases.add(new_subject)


                arg2s = extraction["arg2s"]
                for arg2 in arg2s:
                    arg2_text = arg2["text"]
                    if self.should_extract_attributes:
                        attribute_specs = self.attribute_extractor.extract_attributes(original_sentence)
                        if "attributes" in attribute_specs:
                            attributes = attribute_specs["attributes"]
                            for attribute in attributes:
                                if "unit" not in attribute:
                                    attribute["unit"] = None
                                if "value" not in attribute:
                                    continue
                                if "name" not in attribute:
                                    continue
                                bddAttribute = BDDAttribute(subject = new_subject,
                                                            category=attribute["name"],
                                                            value=attribute["value"],
                                                            unit=attribute["unit"])
                                self.bdd_attributes.append(bddAttribute)
                    # processed_attribute_value = self.preprocessor.attribute_value_extract_phrase(arg2_text)
                    # if processed_attribute_value:
                    #     bddAttribute = BDDAttribute(name = new_subject, value=processed_attribute_value)
                    #     self.bdd_attributes.append(bddAttribute)
                    #     print("Attribute: ", bddAttribute)
                    #     print("Original Sentence: ", original_sentence)
                    #     print("Original Relationship", relationship)
                    processed_object = self.process_phrase_as_noun(arg2_text)
                    if not processed_object or len(processed_object) == 0:
                        # Skip the relationship if the object is empty
                        continue
                    new_object = " ".join(processed_object)
                    if new_object not in sentence_key_phrases:
                        sentence_key_phrases.add(new_object)
                    if relationship['confidence'] > 0.5:
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


        # Normalise the phrase counts
        for phrase in self.phrase_count_dict:
            self.phrase_count_dict[phrase] /= max_count
        for relationship in self.processed_relationships:
            # Normalise the wordnet depths
            for i in range(len(relationship.processed_subject)):
                relationship.processed_subject_props["wordnet_depths"][i] /= max_depth
            for i in range(len(relationship.processed_object)):
                relationship.processed_object_props["wordnet_depths"][i] /= max_depth

        for word in self.wordnet_depth_memo:
            self.wordnet_depth_memo[word] /= max_depth
        
        self.calc_key_phrase_metrics()
        
    
    def calc_key_phrase_metrics(self):
        """Calculate the key phrase metric for each relationship."""
        for relationship in self.processed_relationships:
            # Add the count to the processed props
            relationship.processed_subject_props["count"] = self.phrase_count_dict[relationship.subject]
            relationship.processed_object_props["count"] = self.phrase_count_dict[relationship.object]

            # Calculate the key phrase metric for both the subject and object
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

    def get_key_phrases(self) -> set[str]:
        """Get the key phrases from the filtered relationships."""
        key_phrases = set()
        for relationship in self.filtered_relationships:
            key_phrases.add(relationship.subject)
            key_phrases.add(relationship.object)
        return key_phrases

    def filter_bdd_attributes(self) -> list[BDDAttribute]:
        """Filter the BDD attributes based on the key phrase metric."""
        if not self.bdd_attributes:
            return []
        filtered_bdd_attributes = []
        for bdd_attribute in self.bdd_attributes:
            if bdd_attribute.subject in self.key_phrases:
                filtered_bdd_attributes.append(bdd_attribute)
        return filtered_bdd_attributes
    
    def process_phrase_as_noun(self, text: str) -> list[str]:
        """Process a phrase via the preprocessing rules and limit the phrase length via the tfidfs."""
        preprocessed_text = self.preprocessor.noun_extract_phrase(text)
        # Filter out any words that are not key nouns
        preprocessed_text = [word for word in preprocessed_text if word in self.key_nouns]
        # Remove duplicates while preserving order
        seen = set()
        preprocessed_text = [x for x in preprocessed_text if not (x in seen or seen.add(x))]
        if len(preprocessed_text) > self.phrase_length_limit:
            tf_idf_list = [self.key_nouns[word] for word in preprocessed_text]
            # Get the indices of the phrase_length_limit largest values in the tf_idf_list
            largest_indices = sorted(range(len(tf_idf_list)), key=lambda i: tf_idf_list[i], reverse=True)[:self.phrase_length_limit]
            largest_indices.sort()
            # Use those indices to access the words in the preprocessed_text to form another list
            preprocessed_text = [preprocessed_text[i] for i in largest_indices]
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
                more_synsets = wn.synsets(phrase[i])
                if len(more_synsets) == 0:
                    self.wordnet_depth_memo[phrase[i]] = 0
                    depths.append(0)
                    continue

                max_depth = 0
                for candidate_synset in more_synsets:
                    for possible_synset in more_synsets:
                        similarity = candidate_synset.path_similarity(possible_synset)
                        if similarity:
                            # Track the synset with the maximum depth
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