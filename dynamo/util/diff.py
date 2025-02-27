from dynamo.sysMLAugmenter.types import BDDBlock
import pprint
from prettytable import PrettyTable

def list_diffable_blocks(block_dict_1: dict[str, BDDBlock], block_dict_2: dict[str, BDDBlock]) -> list[str]:
    diffable_blocks = []
    for block_id in block_dict_1.keys():
        if block_id in block_dict_2.keys():
            block_and_source = (block_id, "both_sources")
            diffable_blocks.append(block_and_source)
        else:
            block_and_source = (block_id, "source_1")
            diffable_blocks.append(block_and_source)
    for block_id in block_dict_2.keys():
        if block_id not in block_dict_1.keys():
            block_and_source = (block_id, "source_2")
            diffable_blocks.append(block_and_source)
    diffable_blocks.sort(key=lambda x: x[0])
    print("Here are the blocks to diff from both sources:")
    pprint.pprint(diffable_blocks)
    return diffable_blocks

def diff_blocks(block_1: BDDBlock, block_2: BDDBlock) -> None:
    if block_1.block_name != block_2.block_name:
        print(f"Block Name: {block_1.block_name} != {block_2.block_name}")
    if block_1.isAugmented != block_2.isAugmented:
        print(f"Is Augmented: {block_1.isAugmented} != {block_2.isAugmented}")
    if block_1.operations != block_2.operations:
        print(f"Shared Operations: {block_1.operations.intersection(block_2.operations)}")
        print(f"Unique Operations in Block 1: {block_1.operations - block_2.operations}")
        print(f"Unique Operations in Block 2: {block_2.operations - block_1.operations}")
    if block_1.general_parents != block_2.general_parents:
        print(f"Shared General Parents: {block_1.general_parents.intersection(block_2.general_parents)}")
        print(f"Unique General Parents in Block 1: {block_1.general_parents - block_2.general_parents}")
        print(f"Unique General Parents in Block 2: {block_2.general_parents - block_1.general_parents}")
    if block_1.special_children != block_2.special_children:
        print(f"Shared Special Children: {block_1.special_children.intersection(block_2.special_children)}")
        print(f"Unique Special Children in Block 1: {block_1.special_children - block_2.special_children}")
        print(f"Unique Special Children in Block 2: {block_2.special_children - block_1.special_children}")
    if block_1.composite_parents != block_2.composite_parents:
        print(f"Shared Composite Parents: {block_1.composite_parents.intersection(block_2.composite_parents)}")
        print(f"Unique Composite Parents in Block 1: {block_1.composite_parents - block_2.composite_parents}")
        print(f"Unique Composite Parents in Block 2: {block_2.composite_parents - block_1.composite_parents}")
    if block_1.reference_parents != block_2.reference_parents:
        print(f"Shared Reference Parents: {block_1.reference_parents.intersection(block_2.reference_parents)}")
        print(f"Unique Reference Parents in Block 1: {block_1.reference_parents - block_2.reference_parents}")
        print(f"Unique Reference Parents in Block 2: {block_2.reference_parents - block_1.reference_parents}")
    if block_1.reference_children != block_2.reference_children:
        print(f"Shared Reference Children: {block_1.reference_children.intersection(block_2.reference_children)}")
        print(f"Unique Reference Children in Block 1: {block_1.reference_children - block_2.reference_children}")
        print(f"Unique Reference Children in Block 2: {block_2.reference_children - block_1.reference_children}")
    if block_1.attributes != block_2.attributes:
        print(f"Shared Attributes: {block_1.attributes.intersection(block_2.attributes)}")
        print(f"Unique Attributes in Block 1: {block_1.attributes - block_2.attributes}")
        print(f"Unique Attributes in Block 2: {block_2.attributes - block_1.attributes}")
    if block_1.parts != block_2.parts:
        print(f"Shared Parts: {block_1.parts.intersection(block_2.parts)}")
        print(f"Unique Parts in Block 1: {block_1.parts - block_2.parts}")
        print(f"Unique Parts in Block 2: {block_2.parts - block_1.parts}")
    print("\n")

def compare_blocks_visually(block_1: BDDBlock, block_2: BDDBlock) -> None:
    table = PrettyTable()
    table.field_names = ["Property", "Block 1", "Block 2"]

    properties = [
        ("Block Name", block_1.block_name, block_2.block_name),
        ("Is Augmented", block_1.isAugmented, block_2.isAugmented),
        ("Operations", block_1.operations, block_2.operations),
        ("General Parents", block_1.general_parents, block_2.general_parents),
        ("Special Children", block_1.special_children, block_2.special_children),
        ("Composite Parents", block_1.composite_parents, block_2.composite_parents),
        ("Reference Parents", block_1.reference_parents, block_2.reference_parents),
        ("Reference Children", block_1.reference_children, block_2.reference_children),
        ("Attributes", block_1.attributes, block_2.attributes),
        ("Parts", block_1.parts, block_2.parts)
    ]

    for prop in properties:
        table.add_row([prop[0], prop[1], prop[2]])

    print(table)
    