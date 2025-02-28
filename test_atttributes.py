import pathlib
import yaml
from dynamo.sysMLAugmenter.types import BDDBlock, BDDAttribute
from dynamo.sysMLAugmenter.util import generate_digraph
from dynamo.cache.core import Cache
from dynamo.cache.cacheComponents import getCacheName, CacheComponent
from dynamo.tester.attributeTester import AttributeTester

yaml_path = pathlib.Path(__file__).parent / 'Assets' / 'FlyingMachines' / 'ground_truth' / 'chapter_16_blocks_with_attrs.yaml'
CACHE_DIR = './jsoncaches'
cache = Cache(CACHE_DIR)
corpus_id = "FlyingMachines"
corpus_dir_id = "chapters"
chosen_document_name = "chapter_16_resolved.txt"
block_dict = cache.get_value(getCacheName(corpus_id, chosen_document_name, CacheComponent.BDD_BLOCK_DICT), 'bdd_block_dict')
block_dict = {block_name: BDDBlock.fromJSON(block) for block_name, block in block_dict.items()}

with open(yaml_path, 'r') as file:
    ground_truth = yaml.safe_load(file)

ground_truth_dict = { block.get('block_name'):BDDBlock.fromYAML(block) for block in ground_truth.get('blocks')}

show_digraph = True
if show_digraph:
    digraph = generate_digraph(ground_truth_dict.values())
    digraph.render(filename='flying_machine_chapter_16_ground_attr', format='png', cleanup=True)
    extracted_digraph = generate_digraph(block_dict.values(), without_connections=True)
    extracted_digraph.render(filename='flying_machine_chapter_16_extracted_attr', format='png', cleanup=True)

attributeTester = AttributeTester()
exact_compare_results = attributeTester.compare_block_dict(ground_truth_dict, block_dict)
# print(ground_truth_dict)
print(f"Block Dict Recall: {exact_compare_results}")

nonexact_comparison_results = attributeTester.compare_block_dict_nonexact(ground_truth_dict, block_dict)
print(f"Block Dict Recall Non-Exact: {nonexact_comparison_results}")