from dynamo.relationshipExtractor.types import TypedRelationship, RelationshipType
from enum import Enum
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Synset
from graphviz import Digraph
import pandas as pd
from dynamo.sysMLAugmenter.types import BDDBlock, BDDRelations, BDDGraph, BDDAttribute
from dynamo.sysMLAugmenter.util import generate_digraph

    
    # def add_directed_edge(self, from_block: str, to_block: str, relation: BDDRelations):
    #     if from_block not in self.directed_edges:
    #         self.directed_edges[from_block] = [(to_block, relation)]
    #     self.directed_edges[from_block].append((to_block, relation))

class BDDAugmenter:
    def __init__(self, typed_relationships: list[TypedRelationship],
                 noun_tf_idf_scores: dict[str, float],
                 noun_wordnet_scores: dict[str, float],
                 bdd_plot_word: str,
                 bdd_attributes: list[BDDAttribute] = {},
                 tokenized_sentences: list[str] = [],
                 bdd_plot_path: str = "chapter_13.txt",
                 plot_full_bdd: bool = False):
        self.typed_relationships = typed_relationships
        self.bdd_attributes: list[BDDAttribute] = bdd_attributes

        if tokenized_sentences:
            enumerated_sentences = enumerate(tokenized_sentences)
            self.from_sentence_to_number = {sentence: number for number, sentence in enumerated_sentences}
        else:
            self.from_sentence_to_number = {}

        self.bdd_graph = BDDGraph()
        print("Constructing BDD Graph")
        self.construct_bdd_graph()
        print("BDD Graph Constructed")
        self.bdd_plot_word = bdd_plot_word
        self.bdd_plot_path = bdd_plot_path
        
        # we need to pass in the wordnet and tf_idf scores of the nouns here
        self.noun_tf_idf_scores = noun_tf_idf_scores
        self.noun_wordnet_scores = noun_wordnet_scores

        # I think I need to assemble the relationships into blocks and into some nice graph here before identifying the top level phrases or else the computational inefficiency will crash this 
        self.top_level_phrases = self.identify_top_level_phrases()
        # print(self.top_level_phrases)

        self.abstract_top_level_phrases()
        print("Top Level Phrases Abstracted")

        # At this point all the top level phrases are unigrams
        self.top_level_phrases = self.identify_top_level_phrases()
        # print(self.top_level_phrases)
        print("Begin Relationship Augmentation")

        self.augment_relationships()
        print("Relationships Augmented")
        self.top_level_phrases = self.identify_top_level_phrases()
        self.augment_phrases()
        print("Phrases Augmented")

        for name in self.get_all_block_names():
            print(name, len(self.get_blocks_from_root(name)))
        # print(len(self.bdd_graph.block_dict))
        # print(self.get_all_block_names())
        if plot_full_bdd:
            self.plot_full_bdd()
        else:
            self.plot_bdd_with_root(bdd_plot_word)
        # self.plot_full_bdd()
    

    def get_blocks_with_num_blocks_from_root(self) -> dict[str, int]:
        blocks_with_num_blocks_from_root = {}
        for block_name in self.get_all_block_names():
            blocks_with_num_blocks_from_root[block_name] = len(self.get_blocks_from_root(block_name))
        return blocks_with_num_blocks_from_root

    def get_all_block_names(self) -> set[str]:
        return set(self.bdd_graph.block_dict.keys())
    
    def plot_bdd_with_root(self, root: str) -> None:
        if root not in self.bdd_graph.block_dict:
            print("Root not found in the block dict")
            print("Here are the available roots with the number of blocks from them")
            print(self.get_blocks_with_num_blocks_from_root())
            # print(pd.DataFrame(self.get_blocks_with_num_blocks_from_root()))
            return
        all_blocks_from_root = self.get_blocks_from_root(root)
        print(len(all_blocks_from_root))
        self.plot_full_bdd(all_blocks_from_root)

    def get_blocks_from_root(self, root: str) -> set[BDDBlock]:
        all_blocks_from_root = set()
        block_names_from_root = set()
        queue = [root]
        while queue:
            current_block_name = queue.pop(0)
            current_block = self.bdd_graph.block_dict[current_block_name]
            all_blocks_from_root.add(current_block)
            if current_block.block_name in block_names_from_root:
                continue
            block_names_from_root.add(current_block.block_name)
            for special_child in current_block.special_children:
                queue.append(special_child)
            for part in current_block.parts:
                queue.append(part)
            # for reference_child in current_block.reference_children:
            #     queue.append(reference_child)
        return all_blocks_from_root



    def plot_full_bdd(self, blocks: set[BDDBlock] = []) -> None:
        """ this is often too large to work with """
        if not blocks:
            blocks = set(self.bdd_graph.block_dict.values())
        bdd = generate_digraph(blocks)

        print("Rendering start")
        bdd.render(f"Assets/bddDiagrams/{self.bdd_plot_path}")
        print("Rendering end")

    def construct_bdd_graph(self) -> None:
        for relationship in self.typed_relationships:

            subject_operations = set()
            subject_general_parents = set()
            subject_special_children = set()
            subject_composite_parents = set()
            subject_reference_children = set()
            subject_parts = set()
            subject_operation_sentences : dict[str, list[int]] = {}
            subject_other_sentences = set()

            object_general_parents = set()
            object_special_children = set()
            object_composite_parents = set()
            object_reference_parents = set()
            object_parts = set()
            object_other_sentences = set()

            for relationship_type in relationship.relTypes:
                match relationship_type:
                    case RelationshipType.OPERATION:
                        subject_operations.add(relationship.relation)
                    case RelationshipType.COMPOSITE_SUBJECT_OWNS_OBJECT:
                        object_composite_parents.add(relationship.subject)
                        subject_parts.add(relationship.object)
                    case RelationshipType.COMPOSITE_OBJECT_OWNS_SUBJECT:
                        object_parts.add(relationship.subject)
                        subject_composite_parents.add(relationship.object)
                    case RelationshipType.GENERAL_SUBJECT_TO_SPECIAL_OBJECT:
                        object_general_parents.add(relationship.subject)
                        subject_special_children.add(relationship.object)
                    case RelationshipType.SPECIAL_SUBJECT_TO_GENERAL_OBJECT:
                        subject_general_parents.add(relationship.object)
                        object_special_children.add(relationship.subject)
                    case RelationshipType.REFERENCE_ASSOCIATION:
                        object_reference_parents.add(relationship.subject)
                        subject_reference_children.add(relationship.object)
            if len(self.from_sentence_to_number):
                if RelationshipType.OPERATION in relationship.relTypes:
                    if relationship.relation in subject_operation_sentences:
                        subject_operation_sentences[relationship.relation].append(relationship.original_sentence)
                    else:
                        subject_operation_sentences[relationship.relation] = [relationship.original_sentence]
                subject_other_sentences.add(relationship.original_sentence)
                object_other_sentences.add(relationship.original_sentence)
                
            subject_block = BDDBlock(relationship.subject,
                                     operations=subject_operations,
                                     general_parents=subject_general_parents,
                                    special_children=subject_special_children,
                                     composite_parents=subject_composite_parents,
                                    reference_children=subject_reference_children,
                                     parts=subject_parts,
                                     operation_sentences=subject_operation_sentences,
                                     other_sentences=subject_other_sentences)
            self.bdd_graph.add_or_update_block(subject_block)
            object_block = BDDBlock(relationship.object,
                                     general_parents=object_general_parents,
                                    special_children=object_special_children,
                                     composite_parents=object_composite_parents,
                                     reference_parents=object_reference_parents,
                                     parts=object_parts,
                                     other_sentences=object_other_sentences)
            self.bdd_graph.add_or_update_block(object_block)
        self.update_blocks_with_attributes()
    
    def update_blocks_with_attributes(self) -> None:
        for attribute in self.bdd_attributes:
            if attribute.subject in self.bdd_graph.block_dict:
                self.bdd_graph.block_dict[attribute.subject].attributes.add(attribute)

    def identify_top_level_phrases(self) -> list[str]:
        # identify the top level phrases
        all_blocks = self.bdd_graph.block_dict.values()
        top_level_phrases = []
        for block in all_blocks:
            # Sub-blocks are blocks that  are at the part end of a composite relationship 
            # or at the specialised end of a generalisation relationship
            if not block.general_parents and not block.composite_parents:
                top_level_phrases.append(block.block_name)
        return top_level_phrases

    def abstract_top_level_phrases(self) -> None:
        # abstract the top level phrases
        phrases_to_abstract = [phrase.split() for phrase in self.top_level_phrases]
        phrases_to_abstract = [phrase for phrase in phrases_to_abstract if len(phrase) > 1]
        while phrases_to_abstract:
            phrases_to_abstract = self.abstract_phrases(phrases_to_abstract)
    
    def abstract_phrases(self, phrases_to_abstract: list[list[str]]) -> list[list[str]]:
        new_phrases = []
        for phrase in phrases_to_abstract:
            if not phrase or len(phrase) == 1:
                continue
            word_scores = [0 for _ in range(len(phrase))]
            for i in range(len(phrase)):
                word_scores[i] = self.noun_tf_idf_scores[phrase[i]] + self.noun_wordnet_scores[phrase[i]]
            min_index = word_scores.index(min(word_scores))
            if min_index == len(phrase) - 1:
                new_phrase = phrase[:min_index]
            else:
                new_phrase = phrase[:min_index] + phrase[min_index + 1:]
            old_phrase = " ".join(phrase)
            stringified_new_phrase = " ".join(new_phrase)
            self.bdd_graph.add_or_update_block(BDDBlock(old_phrase,
                                               general_parents={stringified_new_phrase}))
            self.bdd_graph.add_or_update_block(BDDBlock(stringified_new_phrase, special_children={old_phrase}, isAugmented=True))
            new_phrases.append(new_phrase)
        return new_phrases

    def augment_relationships(self) -> None:
        for phrase in self.top_level_phrases:
            phrase_synsets = wn.synsets(phrase)
            if not phrase_synsets:
                continue
            for synset in phrase_synsets:
                for hyponyms in synset.hyponyms():
                    for lemma in hyponyms.lemma_names():
                        if lemma != phrase and lemma in self.top_level_phrases:
                            # this means that the current phrase is specialised by this lemma
                            self.bdd_graph.add_or_update_block(BDDBlock(lemma,
                                               general_parents={phrase}))
                            self.bdd_graph.add_or_update_block(BDDBlock(phrase,
                                                    special_children={lemma}))
                
                for hypernyms in synset.hypernyms():
                    for lemma in hypernyms.lemma_names():
                        if lemma != phrase and lemma in self.top_level_phrases:
                            # this means that the current phrase is generalised by this lemma
                            self.bdd_graph.add_or_update_block(BDDBlock(phrase,
                                               general_parents={lemma}))
                            self.bdd_graph.add_or_update_block(BDDBlock(lemma,
                                                    special_children={phrase}))
                
                for meronyms in synset.part_meronyms():
                    for lemma in meronyms.lemma_names():
                        if lemma != phrase and lemma in self.top_level_phrases:
                            # this means that the current lemma is a part of the current phrase
                            self.bdd_graph.add_or_update_block(BDDBlock(phrase,
                                               parts={lemma}))
                            self.bdd_graph.add_or_update_block(BDDBlock(lemma,
                                                  composite_parents={phrase}))
                
                for holonyms in synset.part_holonyms():
                    for lemma in holonyms.lemma_names():
                        if lemma != phrase and lemma in self.top_level_phrases:
                            # this means that the current phrase is a part of the current lemma
                            print(f"Holonym Augmentation: Lemma {lemma} is a holonym of {phrase}")
                            self.bdd_graph.add_or_update_block(BDDBlock(lemma,
                                               parts={phrase}))
                            self.bdd_graph.add_or_update_block(BDDBlock(phrase,
                                                  composite_parents={lemma}))
        pass

    def augment_phrases(self) -> None:
        # augment the phrases
        for i in range(len(self.top_level_phrases)):
            for j in range(i + 1, len(self.top_level_phrases)):
                phrase1 = self.top_level_phrases[i]
                phrase2 = self.top_level_phrases[j]
                # Synsets are ordered nouns first and by most frequent usage
                phrase1_synsets : list[Synset] = wn.synsets(phrase1)
                phrase2_synsets : list[Synset] = wn.synsets(phrase2)
                if not phrase1_synsets or not phrase2_synsets:
                    continue
                lowest_common_hypernyms = phrase1_synsets[0].lowest_common_hypernyms(phrase2_synsets[0])
                if not lowest_common_hypernyms:
                    continue
                lowest_common_hypernym = lowest_common_hypernyms[0]
                new_general_lemma = lowest_common_hypernym.lemma_names()[0]
                if new_general_lemma not in self.top_level_phrases:
                    self.bdd_graph.add_or_update_block(BDDBlock(phrase1,
                                               general_parents={new_general_lemma}))
                    self.bdd_graph.add_or_update_block(BDDBlock(phrase2,
                                               general_parents={new_general_lemma}))
                    self.bdd_graph.add_or_update_block(BDDBlock(new_general_lemma, special_children= {phrase1, phrase2} ,isAugmented=True))
                    print(f"Generalisation Augmentation: {phrase1} and {phrase2} are generalised by {new_general_lemma}")
