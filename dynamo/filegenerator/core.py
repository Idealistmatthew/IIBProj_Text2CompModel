from dynamo.sysMLAugmenter.types import BDDBlock
from pathlib import Path
import os

class FileGenerator:
    def __init__(self, block_dict: dict[str, BDDBlock], target_dir: Path, system_name: str):
        self.blocks = block_dict
        self.target_dir = target_dir
        self.system_name = system_name
        self.system_dir = target_dir / system_name
        if not self.system_dir.exists():
            os.makedirs(self.system_dir)
        
        top_level_blocks = self.find_top_level_blocks()
        for block in top_level_blocks:
            self.generate_block_code(block, self.system_dir)
    
    def find_top_level_blocks(self) -> list[BDDBlock]:
        top_level_blocks = []
        for block_name, block in self.blocks.items():
            if not block.general_parents and not block.composite_parents:
                top_level_blocks.append(block)
        return top_level_blocks

    def generate_block_code(self, block: BDDBlock, dir: Path):
        if block.parts:
            part_dir_name = block.block_name + "_parts"
            part_dir = dir / part_dir_name
            if not part_dir.exists():
                os.makedirs(part_dir)
            for part in block.parts:
                if part in self.blocks:
                    part_block = self.blocks[part]
                    self.generate_block_code(part_block, part_dir)
        if block.special_children:
            for special_child in block.special_children:
                if special_child in self.blocks:
                    special_child_block = self.blocks[special_child]
                    self.generate_block_code(special_child_block, dir)
        block_file = dir / (block.block_name + ".py")
        with open(block_file, 'w') as f:
            f.write(f"from dynamo.sysMLAugmenter.types import BDDBlock, BDDAttribute\n\n")
            f.write("Generated file")