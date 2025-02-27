from dynamo.sysMLAugmenter.types import BDDBlock
from pathlib import Path
from jinja2 import FileSystemLoader, Environment
import os

def space_str_to_camel_case(space_str: str) -> str:
    space_str = space_str.replace("-", " ")
    space_str = space_str.replace("_", " ")
    space_str = space_str.title()
    return space_str.replace(" ", "")

class FileGenerator:
    def __init__(self, block_dict: dict[str, BDDBlock], target_dir: Path, system_name: str):
        self.blocks = block_dict
        self.target_dir = target_dir
        self.system_name = system_name
        self.system_dir = target_dir / system_name
        templates_path = Path(__file__).resolve().parent / 'templates'
        loader = FileSystemLoader(templates_path)
        env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        class_template = 'class.jinja2'
        self.class_template = env.get_template(class_template)
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
    
    def get_rendered_text(self, block: BDDBlock) -> str:
        className = space_str_to_camel_case(block.block_name)
        attributes = []
        for attribute in block.attributes:
            attributes.append({
                'category': attribute.category,
                'value': attribute.value,
                'unit': attribute.unit,
                'isNumeric': str(attribute.value).isnumeric()
            })
        parts = []
        for part in block.parts:
            parts.append({
                'name': space_str_to_camel_case(part),
                'classname': space_str_to_camel_case(part)
            })
        methods = []
        for operation in block.operations:
            methods.append({
                'name': space_str_to_camel_case(operation),
                'parameters': [],
                'body': None
            })
        general_parents = []
        for general_parent in block.general_parents:
            if general_parent in self.blocks:
                general_block = self.blocks[general_parent]
                if not general_block.isAugmented:
                    general_parents.append(space_str_to_camel_case(general_parent))
        return self.class_template.render(className =className,
                                          attributes = attributes,
                                          parts = parts,
                                          general_parents = general_parents,
                                          methods = methods)

    def generate_block_code(self, block: BDDBlock, dir: Path):

        if block.parts:
            part_dir_name = space_str_to_camel_case(block.block_name) + "_parts"
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
        block_file = dir / (space_str_to_camel_case(block.block_name) + ".py")
        if block.isAugmented:
            print("Block is augmented, skipping")
            return
        with open(block_file, 'w') as f:
            f.write(self.get_rendered_text(block))