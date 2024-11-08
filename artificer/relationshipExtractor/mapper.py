from artificer.relationshipExtractor.types import Relationship, RelationshipType, TypedRelationship
from nltk.corpus import wordnet as wn

class RelationshipMapper:
    def __init__(self, relationships: list[Relationship], relationship_score_diff_tresh: float = 0.5):
        self.relationships = relationships
        self.relationship_score_diff_tresh = relationship_score_diff_tresh
        self.composite_keywords = ['comprise', 'partially', 'voice', 'break', 'involve', 'division', 'represent', 'constituent', 'unharmed', 'moderate', 'set_off', 'make_up', 'break_up', 'parting', 'let_in', 'unhurt', 'ask', 'whole', 'unscathed', 'postulate', 'take_off', 'stop', 'imply', 'lie', 'hold_back', 'separate', 'piece', 'be', 'hold', 'wholly', 'set_out', 'totally', 'all', 'bear', 'start_out', 'entirely', 'section', 'contribution', 'disunite', 'persona', 'require', 'check', 'hold_in', 'depart', 'call_for', 'unit', 'incorporate', 'carry', 'altogether', 'hale', 'part', 'turn_back', 'split_up', 'region', 'need', 'curb', 'arrest', 'admit', 'regard', 'affect', 'dwell', 'set_forth', 'office', 'lie_in', 'necessitate', 'solid', 'unanimous', 'contain', 'include', 'function', 'role', 'split', 'completely', 'theatrical_role', 'component_part', 'start', 'component', 'character', 'control', 'percentage', 'constitute', 'take', 'portion', 'partly', 'demand', 'consist', 'divide', 'share']
        # print(self.composite_keywords)
        self.typed_relationships = []
        self.map_relationships()
    
    def map_relationships(self):
        for relationship in self.relationships:
            relationship_types = self.map_relationship(relationship)
            new_typed_relationship = TypedRelationship(relationship, relationship_types)
            self.typed_relationships.append(new_typed_relationship)

    def map_relationship(self, relationship: Relationship):
        relationship_types = [RelationshipType.OPERATION]
        if self.composite_relation(relationship.relation):
            relationship_types.append(RelationshipType.COMPOSITE_SUBJECT_OWNS_OBJECT)
            return relationship_types
        if self.overlap(relationship.subject, relationship.object):
            if len(relationship.processed_subject) < len(relationship.processed_object):
                relationship_types.append(RelationshipType.GENERAL_SUBJECT_TO_SPECIAL_OBJECT)
            else:
                relationship_types.append(RelationshipType.SPECIAL_SUBJECT_TO_GENERAL_OBJECT)
            return relationship_types
        isReference, doesSubjectOwnObject = self.scoreAssociation(relationship)
        if isReference:
            if doesSubjectOwnObject:
                relationship_types.append(RelationshipType.COMPOSITE_OBJECT_OWNS_SUBJECT)
            else:
                relationship_types.append(RelationshipType.COMPOSITE_SUBJECT_OWNS_OBJECT)
            return relationship_types
        relationship_types.append(RelationshipType.REFERENCE_ASSOCIATION)
        return relationship_types
            
    def composite_relation(self, relation: str):
        # check using Wordnet for words like include that define composite relationships
        relation_synsets = wn.synsets(relation)
        for syn in relation_synsets:
            lemma_names = syn.lemma_names()
            for lemma in lemma_names:
                if lemma in self.composite_keywords:
                    print(relation)
                    return True

    def overlap(self, subject: str, object: str):
        # check if the subject and object overlap
        subject_words = subject.split()
        object_words = object.split()
        if all(word in subject_words for word in object_words):
            return True
        if all(word in object_words for word in subject_words):
            return True
        return False

    def scoreAssociation(self, relationship: Relationship) -> tuple[bool, bool]:
        # check if the score difference of the relationship
        if relationship.processed_subject_props['key_phrase_metric'] - relationship.processed_object_props['key_phrase_metric'] > self.relationship_score_diff_tresh:
            isReference = True
            isSubjectOwnsObject = True
            return isReference, isSubjectOwnsObject
        if relationship.processed_object_props['key_phrase_metric'] - relationship.processed_subject_props['key_phrase_metric'] > self.relationship_score_diff_tresh:
            isReference = True
            isSubjectOwnsObject = False
            return isReference, isSubjectOwnsObject
        isReference = False
        isSubjectOwnsObject = False
        return isReference, isSubjectOwnsObject
    

    # Only used this to get the keywords the first time, so I could hardcode them in the composite_keywords list
    def get_composite_keywords(self):
        """
        Generate a list of composite keywords by extracting synonyms from WordNet for each base word.
        
        Parameters:
        base_words (list): List of words indicating composite relationships.
        
        Returns:
        set: A set of words suggesting composite relationships.
        """
        base_words = ["part", "whole", "include", "contain", "consist", "comprise", "involve"]
        composite_keywords = set()
        
        for word in base_words:
            # Get synsets for each word
            for synset in wn.synsets(word):
                # Add lemma names (synonyms) of each synset to the composite keywords

                word_synsets = wn.synsets(word)
                for syn in word_synsets:
                    lemma_names = syn.lemma_names()
                    for lemma in lemma_names:
                        composite_keywords.add(lemma)
                # Optionally, explore hypernyms and hyponyms for more related terms
                # for hypernym in synset.hypernyms():
                #     for lemma in hypernym.lemmas():
                #         composite_keywords.add(lemma.name())
                # for hyponym in synset.hyponyms():
                #     for lemma in hyponym.lemmas():
                #         composite_keywords.add(lemma.name())
        # Filter duplicates and return as a set
        return composite_keywords

if __name__ == "__main__":
    relationshipMapper = RelationshipMapper([])