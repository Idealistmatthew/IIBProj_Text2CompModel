from artificer.relationshipExtractor.types import TypedRelationship
from typing import Enum

class BDDBlock:
    def __init__(self, block_name: str, isAugmented: bool = False):
        self.block_name = block_name
        self.isAugmented = isAugmented
        self.operations = []
        self.general_parents = []
        self.composite_parents = []
        self.parts = []

class BDDRelations(Enum):
    COMPOSITE = 1
    GENERALIZATION = 2
    AUGMENTED_GENERALIZATION = 3

class BDDGraph:
    def __init__(self):
        self.block_dict = {}
        self.directed_edges: dict[str, list[tuple[str, BDDRelations]]] = {}
    
    def add_block(self, block: BDDBlock):
        self.block_dict[block.block_name] = block
    
    def add_directed_edge(self, from_block: str, to_block: str, relation: BDDRelations):
        if from_block not in self.directed_edges:
            self.directed_edges[from_block] = [(to_block, relation)]
        self.directed_edges[from_block].append((to_block, relation))

class BDDAugmenter:
    def __init__(self, typed_relationships: list[TypedRelationship]):
        self.typed_relationships = typed_relationships

        # I think I need to assemble the relationships into blocks and into some nice graph here before identifying the top level phrases or else the computational inefficiency will crash this 


        self.top_level_phrases = self.identify_top_level_phrases()





    def identify_top_level_phrases() -> list[str]:
        # identify the top level phrases
        pass