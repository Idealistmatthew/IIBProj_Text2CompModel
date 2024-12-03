from enum import Enum
from dynamo.sysMLAugmenter.types import BDDAttribute

class RelationshipType(Enum):
    OPERATION = 1 # is by default according to the paper
    COMPOSITE_SUBJECT_OWNS_OBJECT = 2
    COMPOSITE_OBJECT_OWNS_SUBJECT = 3
    GENERAL_SUBJECT_TO_SPECIAL_OBJECT = 4 # subject is a general ("editor") and object is a special ("flash editor")
    SPECIAL_SUBJECT_TO_GENERAL_OBJECT = 5
    REFERENCE_ASSOCIATION = 6


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

class SubjectWithAttribute:
    def __init__(self, subject: str, attributes: list[BDDAttribute]):
        self.subject = subject
        self.attributes = attributes

class TypedRelationship(Relationship):
    def __init__(self, 
                 subject: str,
                 processed_subject: list[str],
                 processed_subject_props: dict[str, list[float]],
                 relation: str, 
                 object: str, 
                 processed_object: str, 
                 processed_object_props: dict[str, list[float]],
                 confidence: float, 
                 original_sentence: str,
                 relTypes: list[RelationshipType]):
        super().__init__(subject, processed_subject, processed_subject_props, relation, object, processed_object, processed_object_props, confidence, original_sentence)
        self.relTypes = relTypes
    
    def __init__(self, relationship: Relationship, relType: list[RelationshipType]):
        super().__init__(relationship.subject, relationship.processed_subject, relationship.processed_subject_props, relationship.relation, relationship.object, relationship.processed_object, relationship.processed_object_props, relationship.confidence, relationship.original_sentence)
        self.relTypes = relType
    def __repr__(self):
        return (
            f"Subject: {self.subject}, \n"
            f"Relation: {self.relation}, \n"
            f"Object: {self.object}, \n"
            f"Relationship Type: {self.relTypes}, \n"
            f"Confidence: {self.confidence}, \n"
            f"Original Sentence: {self.original_sentence}\n"
        )