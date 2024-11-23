from artificer.relationshipExtractor.types import Relationship, RelationshipType, TypedRelationship
from nltk.corpus import wordnet as wn

class RelationshipMapper:
    def __init__(self, relationships: list[Relationship], relationship_score_diff_tresh: float = 0.5):
        self.relationships = relationships
        self.relationship_score_diff_tresh = relationship_score_diff_tresh
        self.composite_synsets = self.get_composite_synsets()
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
            if syn in self.composite_synsets:
                return True
        return False

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
    def get_composite_synsets(self):
        """
        Generate a list of composite keywords by extracting synonyms from WordNet for each base word.
        
        Parameters:
        base_words (list): List of words indicating composite relationships.
        
        Returns:
        set: A set of words suggesting composite relationships.
        """
        base_words = ["include", "contain", "consist", "comprise"]
        composite_synsets = set()
        
        for word in base_words:
            # Get synsets for each word
            for synset in wn.synsets(word):
                # Add lemma names (synonyms) of each synset to the composite keywords

                word_synsets = wn.synsets(word)
                for syn in word_synsets:
                    composite_synsets.add(syn)
                # Optionally, explore hypernyms and hyponyms for more related terms
                # for hypernym in synset.hypernyms():
                #     for lemma in hypernym.lemmas():
                #         composite_keywords.add(lemma.name())
                # for hyponym in synset.hyponyms():
                #     for lemma in hyponym.lemmas():
                #         composite_keywords.add(lemma.name())
        # Filter duplicates and return as a set
        return composite_synsets

if __name__ == "__main__":
    relationshipMapper = RelationshipMapper([])