from artificer.relationshipExtractor.types import TypedRelationship, RelationshipType
from enum import Enum
from nltk.corpus import wordnet as wn

class BDDBlock:
    def __init__(self, block_name: str,
                  operations: set[str] = set(),
                    isAugmented: bool = False,
                    general_parents: set[str] = set(),
                    composite_parents: set[str] = set(),
                    reference_parents: set[str] = set(),
                    parts: set[str] = set()):
        self.block_name = block_name
        self.isAugmented = isAugmented
        self.operations = operations
        self.general_parents = general_parents
        self.composite_parents = composite_parents
        self.reference_parents = reference_parents
        self.parts = parts

    def __repr__(self):
        return (
            f"Block Name: {self.block_name}, \n"
            f"Operations: {self.operations}, \n"
            f"General Parents: {self.general_parents}, \n"
            f"Composite Parents: {self.composite_parents}, \n"
            f"Reference Parents: {self.reference_parents}, \n"
            f"Parts: {self.parts}\n"
        )
    
class BDDRelations(Enum):
    COMPOSITE = 1
    GENERALIZATION = 2
    AUGMENTED_GENERALIZATION = 3

class BDDGraph:
    def __init__(self):
        self.block_dict: dict[str, BDDBlock] = {}
        # self.directed_edges: dict[str, list[tuple[str, BDDRelations]]] = {}
    
    def add_or_update_block(self, block: BDDBlock):
        if block.block_name not in self.block_dict:
            self.block_dict[block.block_name] = block
        else:
            self.block_dict[block.block_name] = self.update_block(self.block_dict[block.block_name], block)
    
    def update_block(self, old_block: BDDBlock, new_block: BDDBlock) -> BDDBlock:
        old_block.operations.update(new_block.operations)
        old_block.general_parents.update(new_block.general_parents)
        old_block.composite_parents.update(new_block.composite_parents)
        old_block.reference_parents.update(new_block.reference_parents)
        old_block.parts.update(new_block.parts)
        return old_block
    
    # def add_directed_edge(self, from_block: str, to_block: str, relation: BDDRelations):
    #     if from_block not in self.directed_edges:
    #         self.directed_edges[from_block] = [(to_block, relation)]
    #     self.directed_edges[from_block].append((to_block, relation))

class BDDAugmenter:
    def __init__(self, typed_relationships: list[TypedRelationship],
                 noun_tf_idf_scores: dict[str, float],
                 noun_wordnet_scores: dict[str, float]):
        self.typed_relationships = typed_relationships
        self.bdd_graph = BDDGraph()
        self.construct_bdd_graph()

        # we need to pass in the wordnet and tf_idf scores of the nouns here
        self.noun_tf_idf_scores = noun_tf_idf_scores
        self.noun_wordnet_scores = noun_wordnet_scores

        # I think I need to assemble the relationships into blocks and into some nice graph here before identifying the top level phrases or else the computational inefficiency will crash this 
        self.top_level_phrases = self.identify_top_level_phrases()
        # print(self.top_level_phrases)

        self.abstract_top_level_phrases()

        # At this point all the top level phrases are unigrams
        self.top_level_phrases = self.identify_top_level_phrases()
        # print(self.top_level_phrases)

        print("top_level_phrases before augmenting", self.top_level_phrases)

        self.augment_relationships()

        self.top_level_phrases = self.identify_top_level_phrases()

        print("top_level_phrases after augmenting", self.top_level_phrases)

        # for block in self.bdd_graph.block_dict.values():
        #     print(block)


        # self.augment_relationships()
        # self.augment_phrases()

    def construct_bdd_graph(self) -> None:
        for relationship in self.typed_relationships:

            subject_operations = set()
            subject_general_parents = set()
            subject_composite_parents = set()
            subject_parts = set()

            object_general_parents = set()
            object_composite_parents = set()
            object_reference_parents = set()
            object_parts = set()

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
                    case RelationshipType.SPECIAL_SUBJECT_TO_GENERAL_OBJECT:
                        subject_general_parents.add(relationship.object)
                    case RelationshipType.REFERENCE_ASSOCIATION:
                        object_reference_parents.add(relationship.subject)
                
            subject_block = BDDBlock(relationship.subject,
                                     operations=subject_operations,
                                     general_parents=subject_general_parents,
                                     composite_parents=subject_composite_parents,
                                     parts=subject_parts)
            self.bdd_graph.add_or_update_block(subject_block)
            object_block = BDDBlock(relationship.object,
                                     general_parents=object_general_parents,
                                     composite_parents=object_composite_parents,
                                     reference_parents=object_reference_parents,
                                     parts=object_parts)
            self.bdd_graph.add_or_update_block(object_block)

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
            if not phrase:
                continue
            word_scores = [0 for _ in range(len(phrase))]
            for i in range(len(phrase)):
                word_scores[i] = self.noun_tf_idf_scores[phrase[i]] + self.noun_wordnet_scores[phrase[i]]
            min_index = word_scores.index(min(word_scores))
            if min_index == len(phrase) - 1:
                new_phrase = phrase[:min_index]
            else:
                new_phrase = phrase[:min_index] + phrase[min_index + 1:]
            stringified_new_phrase = " ".join(new_phrase)
            self.bdd_graph.add_or_update_block(BDDBlock(" ".join(phrase),
                                               general_parents={stringified_new_phrase}))
            self.bdd_graph.add_or_update_block(BDDBlock(stringified_new_phrase, isAugmented=True))
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
                            print(f"Hyponym Augmentation: Lemma {lemma} is a hyponym of {phrase}")
                            self.bdd_graph.add_or_update_block(BDDBlock(lemma,
                                               general_parents=set(phrase)))
                
                for hypernyms in synset.hypernyms():
                    for lemma in hypernyms.lemma_names():
                        if lemma != phrase and lemma in self.top_level_phrases:
                            # this means that the current phrase is generalised by this lemma
                            print(f"Hypernym Augmentation: Lemma {lemma} is a hypernym of {phrase}")
                            self.bdd_graph.add_or_update_block(BDDBlock(phrase,
                                               general_parents=set(lemma)))
                
                for meronyms in synset.part_meronyms():
                    for lemma in meronyms.lemma_names():
                        if lemma != phrase and lemma in self.top_level_phrases:
                            # this means that the current lemma is a part of the current phrase
                            print(f"Meronym Augmentation: Lemma {lemma} is a meronym of {phrase}")
                            self.bdd_graph.add_or_update_block(BDDBlock(phrase,
                                               parts=set(lemma)))
                            self.bdd_graph.add_or_update_block(BDDBlock(lemma,
                                                  composite_parents=set(phrase)))
                
                for holonyms in synset.part_holonyms():
                    for lemma in holonyms.lemma_names():
                        if lemma != phrase and lemma in self.top_level_phrases:
                            # this means that the current phrase is a part of the current lemma
                            print(f"Holonym Augmentation: Lemma {lemma} is a holonym of {phrase}")
                            self.bdd_graph.add_or_update_block(BDDBlock(lemma,
                                               parts=set(phrase)))
                            self.bdd_graph.add_or_update_block(BDDBlock(phrase,
                                                  composite_parents=set(lemma)))
        pass

    def augment_phrases(self) -> None:
        # augment the phrases
        for phrase in self.top_level_phrases:
            phrase_synsets = wn.synsets(phrase)

            # find lowest common hypernyms and apply a generalisation relationship
            if not phrase_synsets:
                continue
