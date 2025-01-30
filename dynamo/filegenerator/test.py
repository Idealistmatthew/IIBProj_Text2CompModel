import os
from pathlib import Path
from dynamo.sysMLAugmenter.types import BDDBlock, BDDAttribute

blocks = {
    "Block1":
    BDDBlock(   
        block_name="Block1",
        operations={"op1", "op2"},
        isAugmented=True,
        general_parents={"Block2"},
        special_children={"Block3"},
        attributes={BDDAttribute(subject="subject1" ,category="category1", value="value1", unit="unit1")},
        parts={"part1", "part2"}
    ),
    "Block2":
    BDDBlock(
        block_name="Block2",
        operations={"op3", "op4"},
        isAugmented=False,
        special_children={"Block1"},
        attributes={BDDAttribute(subject="subject2" ,category="category2", value="value2", unit="unit2")}
    ),
    "Block3":
    BDDBlock(
        block_name="Block3",
        operations={"op5", "op6"},
        isAugmented=True,
        general_parents={"Block1"},
        attributes={BDDAttribute(subject="subject3" ,category="category3", value="value3", unit="unit3")}
    ),
    "part1":
    BDDBlock(
        block_name="part1",
        operations={"op7", "op8"},
        composite_parents={"Block1"},
        isAugmented=False,
        attributes={BDDAttribute(subject="subject4" ,category="category4", value="value4", unit="unit4")}
    ),
    "part2":
    BDDBlock(
        block_name="part2",
        operations={"op9", "op10"},
        composite_parents={"Block1"},
        isAugmented=False,
        attributes={BDDAttribute(subject="subject5" ,category="category5", value="value5", unit="unit5")}
    )
}


target_dir = Path(__file__).resolve().parent.parent.parent / 'codegen'

system_name = "FlyingMachines"

system_dir = target_dir / system_name

if not os.path.exists(system_dir):
    os.makedirs(system_dir)

def find_top_level_blocks(blocks: dict[str, BDDBlock]) -> list[BDDBlock]:
    top_level_blocks = []
    for block_name, block in blocks.items():
        if not block.general_parents and not block.composite_parents:
            top_level_blocks.append(block)
    return top_level_blocks

def generate_block_code(block: BDDBlock, dir: Path):
    # print("Generating block", block.block_name)
    if block.parts:
        part_dir_name = block.block_name + "_parts"
        part_dir = dir / part_dir_name
        if not os.path.exists(part_dir):
            os.makedirs(part_dir)
        for part in block.parts:
            if part in blocks:
                part_block = blocks[part]
                generate_block_code(part_block, part_dir)
    if block.special_children:
        for special_child in block.special_children:
            if special_child in blocks:
                special_child_block = blocks[special_child]
                generate_block_code(special_child_block, dir)
    block_file = dir / (block.block_name + ".py")
    with open(block_file, 'w') as f:
        f.write(f"from dynamo.sysMLAugmenter.types import BDDBlock, BDDAttribute\n\n")
        f.write("Generated file")

top_level_blocks = find_top_level_blocks(blocks)


print("Top level blocks:", top_level_blocks)
for block in top_level_blocks:
    generate_block_code(block, system_dir)






    