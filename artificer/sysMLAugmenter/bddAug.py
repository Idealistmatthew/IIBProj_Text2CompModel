from artificer.relationshipExtractor.types import TypedRelationship, RelationshipType
from enum import Enum

EMPTY_SET = set()

class BDDBlock:
    def __init__(self, block_name: str,
                  operations: set[str] = EMPTY_SET,
                    isAugmented: bool = False,
                    general_parents: set[str] = EMPTY_SET,
                    composite_parents: set[str] = EMPTY_SET,
                    reference_parents: set[str] = EMPTY_SET,
                    parts: set[str] = EMPTY_SET):
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
    
    def add_block(self, block: BDDBlock):
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
    def __init__(self, typed_relationships: list[TypedRelationship]):
        self.typed_relationships = typed_relationships
        self.bdd_graph = BDDGraph()
        self.construct_bdd_graph()

        # I think I need to assemble the relationships into blocks and into some nice graph here before identifying the top level phrases or else the computational inefficiency will crash this 
        self.top_level_phrases = self.identify_top_level_phrases()
        print(self.top_level_phrases)

        self.abstract_top_level_phrases()
        self.augment_relationships()
        self.augment_phrases()

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
            self.bdd_graph.add_block(subject_block)
            object_block = BDDBlock(relationship.object,
                                     general_parents=object_general_parents,
                                     composite_parents=object_composite_parents,
                                     reference_parents=object_reference_parents,
                                     parts=object_parts)
            self.bdd_graph.add_block(object_block)


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
        for phrase in self.top_level_phrases:
            block = self.bdd_graph.block_dict[phrase]
            block.isAugmented = True
    
    def augment_relationships(self) -> None:
        pass

    def augment_phrases(self) -> None:
        # augment the phrases
        for block in self.bdd_graph.block_dict.values():
            if block.isAugmented:
                # augment the block
                pass