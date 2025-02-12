import os
from pathlib import Path
from dynamo.sysMLAugmenter.types import BDDBlock, BDDAttribute
from dynamo.filegenerator.core import FileGenerator

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

system_name = "testSystem"

system_dir = target_dir / system_name

if not os.path.exists(system_dir):
    os.makedirs(system_dir)


FileGenerator(blocks, target_dir, system_name)





    