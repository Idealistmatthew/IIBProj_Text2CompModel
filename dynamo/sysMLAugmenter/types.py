from enum import Enum

class BDDAttribute:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return (
            f"Attribute Name: {self.name}, \n"
            f"Attribute Value: {self.value}\n"
        )

class BDDBlock:
    def __init__(self, block_name: str,
                  operations: set[str] = None,
                    isAugmented: bool = False,
                    general_parents: set[str] = None,
                    special_children: set[str] = None,
                    composite_parents: set[str] = None,
                    reference_parents: set[str] = None,
                    reference_children: set[str] = None,
                    attributes: set[BDDAttribute] = None,
                    parts: set[str] = None):
        if not operations:
            operations = set()
        if not general_parents:
            general_parents = set()
        if not special_children:
            special_children = set()
        if not composite_parents:
            composite_parents = set()
        if not reference_parents:
            reference_parents = set()
        if not reference_children:
            reference_children = set()
        if not attributes:
            attributes = set()
        if not parts:
            parts = set()
        self.block_name = block_name
        self.isAugmented = isAugmented
        self.operations = operations
        self.general_parents = general_parents
        self.special_children = special_children
        self.composite_parents = composite_parents
        self.reference_parents = reference_parents
        self.reference_children = reference_children
        self.attributes = attributes
        self.parts = parts

    def __repr__(self):
        return (
            f"Block Name: {self.block_name}, \n"
            f"Operations: {self.operations}, \n"
            f"General Parents: {self.general_parents}, \n"
            f"Special Children: {self.special_children}, \n"
            f"Composite Parents: {self.composite_parents}, \n"
            f"Reference Parents: {self.reference_parents}, \n"
            f"Reference Children: {self.reference_children}, \n"
            f"Parts: {self.parts}\n"
        )

    def to_label(self):
        label_str = "{"+ f"{self.block_name} "
        if self.attributes:
            label_str += "| Attributes:  \\n"
            for attribute in self.attributes:
                label_str += f"{attribute.name}: {attribute.value}  \\n"
        if self.parts:
            label_str += "| Parts:  \\n"
            for part in self.parts:
                label_str += f"{part}  \\n"
        if self.operations:
            label_str += "| Operations:  \\n"
            for operation in self.operations:
                label_str += f"{operation}()  \\n"
        label_str += "}"
        return label_str
    
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
        old_block.special_children.update(new_block.special_children)
        old_block.composite_parents.update(new_block.composite_parents)
        old_block.reference_parents.update(new_block.reference_parents)
        old_block.reference_children.update(new_block.reference_children)
        old_block.parts.update(new_block.parts)
        return old_block