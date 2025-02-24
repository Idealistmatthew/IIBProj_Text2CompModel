from dynamo.cache.core import Cache
from dynamo.cache.cacheComponents import getCacheName, CacheComponent
from dynamo.util.diff import list_diffable_blocks, diff_blocks
from dynamo.sysMLAugmenter.types import BDDBlock
from dynamo.tester.attributeTester import AttributeTester

CACHE_DIR = './jsoncaches'
cache = Cache(CACHE_DIR)
corpus_id = "FlyingMachines"
corpus_dir_id = "chapters"
chosen_document_name_1 = "chapter_16.txt"
block_dict_1 = cache.get_value(getCacheName(corpus_id, chosen_document_name_1, CacheComponent.BDD_BLOCK_DICT), 'bdd_block_dict')
block_dict_1 = {block_name: BDDBlock.fromJSON(block) for block_name, block in block_dict_1.items()}
chosen_document_name_2 = "chapter_16_resolved.txt"
block_dict_2 = cache.get_value(getCacheName(corpus_id, chosen_document_name_2, CacheComponent.BDD_BLOCK_DICT), 'bdd_block_dict')
block_dict_2 = {block_name: BDDBlock.fromJSON(block) for block_name, block in block_dict_2.items()}
# list_diffable_blocks(block_dict_1, block_dict_2)

diff_blocks(block_dict_1['rudder'], block_dict_2['rudder'])

attributeTester = AttributeTester()
attribute_similarity = attributeTester.compare_attributes(block_dict_1['rudder'], block_dict_2['rudder'])
print(f"Attribute Similarity: {attribute_similarity}")
block_dict_recall = attributeTester.compare_block_dict(block_dict_1, block_dict_2)
print(f"Block Dict Recall: {block_dict_recall}")