from dynamo.sysMLAugmenter.types import BDDBlock, BDDAttribute
from dynamo.codeGenerator.core import CodeGenerator, GuessFunctionResult
from pathlib import Path
from jinja2 import FileSystemLoader, Environment
import os
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

def space_str_to_camel_case(space_str: str) -> str:
    space_str = space_str.replace("-", " ")
    space_str = space_str.replace("_", " ")
    space_str = space_str.title()
    return space_str.replace(" ", "")

class FileGenerator:
    def __init__(self,
                 block_dict: dict[str, BDDBlock],
                target_dir: Path,
                  system_name: str,
                  tokenized_sentences: list[str] = None):
        self.blocks = block_dict
        self.target_dir = target_dir
        self.system_name = system_name
        self.system_dir = target_dir / system_name
        self.mask = [-1, 0, 1]
        self.summarizer = TextRankSummarizer()
        self.max_class_sentences = 2
        self.generated = set()
        self.codeGenerator = CodeGenerator()

        tokenized_sentence_enumerated = enumerate(tokenized_sentences)
        self.tokenized_sentence_to_sentence_num = {tokenized_sentence: sentence_num for sentence_num, tokenized_sentence in tokenized_sentence_enumerated}
        self.sentence_num_to_tokenized_sentence = {sentence_num: tokenized_sentence for tokenized_sentence, sentence_num in self.tokenized_sentence_to_sentence_num.items()}
        print(self.sentence_num_to_tokenized_sentence.keys())

        templates_path = Path(__file__).resolve().parent / 'templates'
        loader = FileSystemLoader(templates_path)
        env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        class_template = 'class.jinja2'
        self.class_template = env.get_template(class_template)
        system_template = 'system.jinja2'
        self.system_template = env.get_template(system_template)
        if not self.system_dir.exists():
            os.makedirs(self.system_dir)
        
        top_level_blocks = self.find_top_level_blocks()

        self.numeric_attribute_dict = self.get_numeric_attribute_dict(block_dict)
        self.simulatable_blocks = {}

        self.non_augmented_block_dict = self.make_non_augmented_block_dict(block_dict)
        non_augmented_top_level_blocks = self.find_non_augmented_top_level_blocks()
        
        
        for block in top_level_blocks:
            self.generate_block_code(block, self.system_dir)

        

        self.top_level_block_names = []
        self.non_simulatable_blocks = []
        for block in non_augmented_top_level_blocks:
            if block.block_name not in self.simulatable_blocks:
                self.non_simulatable_blocks.append(block.block_name.title())
            self.top_level_block_names.append(block.block_name.title())
        
        self.generate_system_code(self.system_dir)
    
    def get_numeric_attribute_dict(self, block_dict: dict[str, BDDBlock]) -> dict[str, list[dict[str, str]]]:
        numeric_attribute_dict = {}
        for block_name, block in block_dict.items():
            for attribute in block.attributes:
                if str(attribute.value).replace(".","").isnumeric():
                    if block_name not in numeric_attribute_dict:
                        numeric_attribute_dict[block_name] = [space_str_to_camel_case(attribute.category)]
                    else:
                        numeric_attribute_dict[block_name].append(space_str_to_camel_case(attribute.category))
        return numeric_attribute_dict
    
    def make_non_augmented_block_dict(self, block_dict: dict[str, BDDBlock]) -> dict[str, BDDBlock]:
        non_augmented_block_dict = {}
        augmented_blocks = set()
        for block_name, block in block_dict.items():
            if not block.isAugmented:
                non_augmented_block_dict[block_name] = block
            else:
                augmented_blocks.add(block_name)
        for block_name, block in non_augmented_block_dict.items():
            for general_parent in list(block.general_parents):
                if general_parent in augmented_blocks:
                    block.general_parents.remove(general_parent)
            for composite_parent in list(block.composite_parents):
                if composite_parent in augmented_blocks:
                    block.composite_parents.remove(composite_parent)
        return non_augmented_block_dict
    
    def find_top_level_blocks(self) -> list[BDDBlock]:
        top_level_blocks = []
        for block_name, block in self.blocks.items():
            if not block.general_parents and not block.composite_parents:
                top_level_blocks.append(block)
        return top_level_blocks
    
    def find_non_augmented_top_level_blocks(self) -> list[BDDBlock]:
        non_augmented_top_level_blocks = []
        for block_name, block in self.non_augmented_block_dict.items():
            if not block.isAugmented and not block.general_parents and not block.composite_parents:
                non_augmented_top_level_blocks.append(block)
        return non_augmented_top_level_blocks

    def summarize_text(self, text: str, num_sentences: int) -> str:
        text = text.replace(".", ". ")
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summary = self.summarizer(parser.document, num_sentences)
        sentence_str = ""
        for sentence in summary:
            sentence_str += str(sentence)
        return sentence_str
    
    def give_contextual_sentences(self, tokenized_sentence: str) -> str:
        current_sentence_idx = self.tokenized_sentence_to_sentence_num.get(tokenized_sentence, -1)
        sentence_idx_in_mask = [mask_num + current_sentence_idx for mask_num in self.mask]
        # print(sentence_idx_in_mask)
        res = "".join([self.sentence_num_to_tokenized_sentence.get(sentence_idx, "") for sentence_idx in sentence_idx_in_mask])
        # print(res)
        return res
    
    def get_attribute_dictionary_from_attribute_set(self, attribute_set: set[BDDAttribute]) -> dict[str, str]:
        attribute_dict = {}
        for attribute in attribute_set:
            attribute_dict[space_str_to_camel_case(attribute.category)] = attribute.value
        return attribute_dict
    
    def get_rendered_text(self, block: BDDBlock) -> str:
        className = space_str_to_camel_case(block.block_name)
        class_comments = "".join([sentence for sentence in block.other_sentences])
        if len(block.other_sentences) > self.max_class_sentences:
            print(f"Warning: Too many sentences in class comments for {block.block_name}")
            class_comments = self.summarize_text(class_comments, self.max_class_sentences)
        attributes = []
        surrounding_numeric_attributes = {}
        for key, value in self.numeric_attribute_dict.items():
            if key != block.block_name:
                surrounding_numeric_attributes[key] = value
        for attribute in block.attributes:
            if str(attribute.value).replace(".","").isnumeric():
                attribute.value = float(attribute.value)
            attributes.append({
                'category': space_str_to_camel_case(attribute.category),
                'value': attribute.value,
                'unit': attribute.unit,
                'isNumeric': str(attribute.value).replace(".","").isnumeric()
            })
        parts = []
        for part in block.parts:
            parts.append({
                'name': space_str_to_camel_case(part),
                'classname': space_str_to_camel_case(part)
            })
        methods = []
        rendered_methods = []
        function_states = []
        module_imports = []
        matched_system_components = []
        for operation in block.operations:
            operation_name = space_str_to_camel_case(operation)
            operation_prompt = "".join([self.give_contextual_sentences(sentence) for sentence in block.operation_sentences[operation]])
            attribute_dict = self.get_attribute_dictionary_from_attribute_set(block.attributes)
            guessed_function : GuessFunctionResult = self.codeGenerator.guess_function(operation_name, attribute_dict, surrounding_numeric_attributes, operation_prompt)
            if guessed_function:
                rendered_methods.append(guessed_function.function_implementation)
                rendered_methods.append(guessed_function.simulate_function)
                function_states.extend(guessed_function.function_states)
                self.simulatable_blocks[className] = {"function_states": guessed_function.function_states}
                module_imports.extend(guessed_function.required_imports)
                matched_system_components.extend(guessed_function.matched_system_components)
            else:
                methods.append({
                'name': operation_name,
                'parameters': [],
                'body': None,
                'comments': operation_prompt
            })
        general_parents = []
        for general_parent in block.general_parents:
            if general_parent in self.blocks:
                general_block = self.blocks[general_parent]
                if not general_block.isAugmented:
                    general_parents.append(space_str_to_camel_case(general_parent))
        add_init_args = None
        add_init_args_str = None
        if function_states:
            add_init_args = [f"initial_{state}" for state in function_states]
            add_init_args_str = ", ".join(add_init_args)
        return self.class_template.render(className =className,
                                          class_comments = class_comments,
                                          attributes = attributes,
                                          parts = parts,
                                          general_parents = general_parents,
                                          methods = methods,
                                          rendered_methods = rendered_methods,
                                          function_states = function_states,
                                          add_init_args = add_init_args_str,
                                          module_imports = module_imports,
                                          matched_system_components = matched_system_components)

    def generate_block_code(self, block: BDDBlock, dir: Path) -> None:
        if block.block_name in self.generated:
            return
        ""
        if block.parts:
            part_dir_name = space_str_to_camel_case(block.block_name) + "_parts"
            part_dir = dir / part_dir_name
            try:
                if not part_dir.exists():
                    os.makedirs(part_dir)
            except Exception as e:
                print(f"Error creating directory {part_dir}")
                print(e)
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
        try:
            with open(block_file, 'w') as f:
                if space_str_to_camel_case(block.block_name) == "RudderBeam":
                    print("Hi")
                    print(block_file)
                f.write(self.get_rendered_text(block))
                self.generated.add(block.block_name)

        except Exception as e:
            print(f"Error writing to file {block_file}")
            print(e)


    def get_system_rendered_text(self) -> str:
        top_level_simulatable_components = []
        function_states = []
        for blockName, block in self.simulatable_blocks.items():
            number_of_states = len(block["function_states"])
            args = ",".join([f"0" for state in block["function_states"]])
            block_res = {
                'name': blockName,
                'args': args,
                'function_states': block["function_states"],
            }
            top_level_simulatable_components.append(block_res)
            for state in block["function_states"]:
                if state not in function_states:
                    function_states.append(state)
        res = self.system_template.render(
            top_level_components=self.top_level_block_names,
            top_level_non_simulatable_components=self.non_simulatable_blocks,
            top_level_simulatable_components=top_level_simulatable_components,
            function_states=function_states,
        )
        return res
        
    
    def generate_system_code(self, dir: Path) -> None:
        system_file = dir / ("System.py")
        rendered_text = self.get_system_rendered_text()
        try:
            with open(system_file, 'w') as f:
                f.write(rendered_text)
        except Exception as e:
            print(f"Error writing to file {system_file}")
            print(e)