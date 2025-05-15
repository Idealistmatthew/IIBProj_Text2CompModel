from enum import Enum
import json
import jsonpickle

class BDDAttribute:
    def __init__(self, subject: str=None, category: str=None, value: str=None, unit: str=None):
        self.subject = subject
        self.category = category
        if type(value) == list:
            value = ' '.join(value)
        self.value = value
        self.unit = unit
    
    # def __repr__(self):
    #     return (
    #         f"Attribute Name: {self.subject}, \n"
    #         f"Attribute Category: {self.category}, \n"
    #         f"Attribute Value: {self.value}\n"
    #         f"Attribute Unit: {self.unit}\n"
    #     )

    def __repr__(self):
        return (
            f"{self.category}: {self.value} {self.unit}"
        )

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    
    def fromJSON(json_str):
        json_obj = json.loads(json_str)
        return BDDAttribute(json_obj['subject'], json_obj['category'], json_obj['value'], json_obj['unit'])
    
    def fromYAML(yaml_dict):
        return BDDAttribute(
            subject=yaml_dict.get('subject'),
            category=yaml_dict.get('category'),
            value=yaml_dict.get('value'),
            unit=yaml_dict.get('unit')
        )

    def __eq__(self, value):
        if isinstance(value, BDDAttribute):
            return (self.category == value.category and
                    self.value == value.value and
                    self.unit == value.unit
                    and self.subject == value.subject)
        return False

    def __hash__(self):
        return hash((self.category, self.value, self.unit, self.subject))

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
                    parts: set[str] = None,
                    operation_sentences: dict[str, list[str]]= {}, 
                    # Sentences are stored based on sentence index because the memory usage is bearable this way
                    other_sentences: set[str] = None):
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
        if not other_sentences:
            other_sentences = set()
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
        self.operation_sentences = operation_sentences
        self.other_sentences = other_sentences

    def __repr__(self):
        return (
            f"Block Name: {self.block_name}, \n"
            f"Operations: {self.operations}, \n"
            f"General Parents: {self.general_parents}, \n"
            f"Special Children: {self.special_children}, \n"
            f"Composite Parents: {self.composite_parents}, \n"
            f"Reference Parents: {self.reference_parents}, \n"
            f"Reference Children: {self.reference_children}, \n"
            f"attributes: {self.attributes}, \n"
            f"Parts: {self.parts}\n"
        )

    def to_label(self):
        label_str = "{"+ f"{self.block_name} "
        if self.attributes:
            label_str += "| Attributes:  \\n"
            for attribute in self.attributes:
                label_str += f"{attribute.category}: {attribute.value} {attribute.unit} \\n"
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
    
    def toJSON(self):
        return jsonpickle.encode(self)
    
    def fromJSON(json_str):
        return jsonpickle.decode(json_str)
    
    def fromYAML(yaml_dict):
        return BDDBlock(
            block_name=yaml_dict.get('block_name'),
            operations=set(yaml_dict.get('operations', [])),
            isAugmented=yaml_dict.get('isAugmented', False),
            general_parents=set(yaml_dict.get('general_parents', [])),
            special_children=set(yaml_dict.get('special_children', [])),
            composite_parents=set(yaml_dict.get('composite_parents', [])),
            reference_parents=set(yaml_dict.get('reference_parents', [])),
            reference_children=set(yaml_dict.get('reference_children', [])),
            attributes=set([BDDAttribute.fromYAML(attr) for attr in yaml_dict.get('attributes', [])]),
            parts=yaml_dict.get('parts', [])
        )

    
class BDDRelations(Enum):
    COMPOSITE = 1
    GENERALIZATION = 2
    AUGMENTED_GENERALIZATION = 3

class BDDGraph:
    def __init__(self):
        self.block_dict: dict[str, BDDBlock] = {}
    
    def update_block_dict(self, block_dict: dict[str, BDDBlock]):
        self.block_dict = block_dict
    
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
        # for rels in new_block.operation_sentences.keys():
        #     if rels in old_block.operation_sentences.keys():
        #         old_block.operation_sentences[rels].extend(new_block.operation_sentences[rels])
        #     else:
        #         old_block.operation_sentences[rels] = new_block.operation_sentences[rels]
        old_block.operation_sentences.update(new_block.operation_sentences)
        old_block.other_sentences.update(new_block.other_sentences)
        return old_block