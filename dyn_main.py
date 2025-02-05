from dynamo.util.chapter_split import split_chapters
import os

from dynamo.cache.core import Cache

from pathlib import Path
from dynamo.preprocessor.core import Preprocessor
from dynamo.keyNounExtractor.core import KeyNounExtractor
from dynamo.relationshipExtractor.core import RelationshipExtractor, RelationshipParser, RelationshipSerialiser
from dynamo.relationshipExtractor.mapper import RelationshipMapper
from dynamo.sysMLAugmenter.bddAug import BDDAugmenter
from dynamo.cache.cacheComponents import getCacheName, CacheComponent
from dynamo.sysMLAugmenter.types import BDDAttribute, BDDBlock
from dynamo.filegenerator.core import FileGenerator

ASSET_DIR = './Assets'
CACHE_DIR = './jsoncaches'
PREPROCESSED_NOUNS_CACHE = 'preprocessed_nouns'

HYPERPARAMS = {
    'tf_idf': 0,
    'relationship': 0.5, # not using this yet since the relationships extracted at the moment are still manageable
    'phrase_length': 3,
    'key_phrase_selection': 0.6,
    'relationship_score_diff_tresh': 0.5
}

def main_loop_to_rel_extraction(corpus_id, corpus_dir_id, document_path): 
    cache = Cache(CACHE_DIR)
    if not corpus_id:
        corpus_id = "FlyingMachines"
    if not corpus_dir_id:
        corpus_dir_id = "chapters"
    corpus_dir =  Path(__file__).resolve().parent / 'Assets' / corpus_id / corpus_dir_id
    preprocessor = Preprocessor(corpus_dir=corpus_dir)

    chosen_document_name = os.path.basename(document_path)
    if corpus_dir != Path(document_path).parent:
        preprocessor.add_chosen_document(document_path, chosen_document_name)

    corpus_document_index_dict = preprocessor.get_chapter_dict()
    print(corpus_document_index_dict)
    chosen_document_num = corpus_document_index_dict[chosen_document_name]
    preprocessor.preprocess()
    
    # print(preprocessor.nouns)
    # print(len(preprocessor.nouns))

    key_noun_extractor = KeyNounExtractor(
        preprocessor.nouns,
                                           chosen_chapter=chosen_document_num,
                                           tf_idf_limit=HYPERPARAMS['tf_idf'])
    cache.set(getCacheName(corpus_id, chosen_document_name, CacheComponent.KEY_NOUNS),
               {'tf_idf': key_noun_extractor.chosen_chapter_tf_idf, 'key_nouns': key_noun_extractor.key_nouns})
    # cache.set(f"{corpus_id}_{chosen_document_name}_key_nouns", {'tf_idf': key_noun_extractor.chosen_chapter_tf_idf
    #                                                                ,'key_nouns': key_noun_extractor.key_nouns})

    relationshipExtractor = RelationshipExtractor(tokenized_sentences = preprocessor.sentence_tokenized_documents, chosen_chapter=chosen_document_num)
    
    cache.set(getCacheName(corpus_id, chosen_document_name, CacheComponent.RAW_RELATIONSHIPS),
                {'relationships': relationshipExtractor.extracted_relationships})

    # cache.set(f"{corpus_id}_{chosen_document_name}_raw_relationships", 
    #           {'relationships': relationshipExtractor.extracted_relationships})

    def new_partition(self):
        # Only run this script if it is a new document to partition

        book_dir = os.path.join(ASSET_DIR, 'FlyingMachines')
        epub_dir = os.path.join(book_dir, 'flying_machines.epub')
        split_chapters(book_dir, epub_dir)

def from_cache_to_Bdd_Diagram(
    corpus_id=None,
    corpus_dir_id=None,
    chosen_document_name=None,
    chosen_document_path=None,
    bdd_plot_chosen_word=None,
    skip_attribute_extraction=False,
    export_key_phrase_path=None
):
    if not corpus_id:
        corpus_id = "FlyingMachines"
    if not corpus_dir_id:
        corpus_dir_id = "chapters"
    if not chosen_document_path:
        chosen_document_path = Path(__file__).resolve().parent / 'Assets' / corpus_id / "resolved_chapters" / "chapter_38_resolved.txt"
    corpus_dir =  Path(__file__).resolve().parent / 'Assets' / corpus_id / corpus_dir_id
    preprocessor = Preprocessor(corpus_dir=corpus_dir)

    chosen_document_name = os.path.basename(chosen_document_path)
    if corpus_dir != Path(chosen_document_path).parent:
        preprocessor.add_chosen_document(chosen_document_path, chosen_document_name)

    chapter_num_dict = preprocessor.get_chapter_dict()
    if not chosen_document_name:
        chosen_document_name = "chapter_38.txt"
    chosen_document_name_without_ext = chosen_document_name.split('.')[0]
    chosen_document_num = chapter_num_dict[chosen_document_name]

    relationships = cache.get_value(getCacheName(corpus_id, chosen_document_name, CacheComponent.RAW_RELATIONSHIPS), 'relationships')
    # relationships = cache.get_value(f"{corpus_id}_{chosen_document_name}_raw_relationships", 'relationships')

    key_nouns: dict[str, float] = cache.get_value(getCacheName(corpus_id, chosen_document_name, CacheComponent.KEY_NOUNS), 'key_nouns')
    # key_nouns: dict[str, float] = cache.get_value(f"{corpus_id}_{chosen_document_name}_key_nouns", 'key_nouns')

    relationshipParser = RelationshipParser(
        relationships,
        preprocessor,
        key_nouns,
        phrase_length_limit=HYPERPARAMS['phrase_length'],
        key_phrase_metric_tresh=HYPERPARAMS['key_phrase_selection'],
        relationship_confidence_tresh=HYPERPARAMS['relationship'],
        should_extract_attributes=not skip_attribute_extraction
    )
    
    if export_key_phrase_path:
        relationshipParser.export_key_phrases(export_key_phrase_path)

    relationshipMapper = RelationshipMapper(
        relationshipParser.filtered_relationships,
        relationship_score_diff_tresh=HYPERPARAMS['relationship_score_diff_tresh']
    )

    if not skip_attribute_extraction:
        BDD_Attributes_jsoned = [attribute.toJSON() for attribute in relationshipParser.bdd_attributes]
        cache.set(getCacheName(corpus_id, chosen_document_name, CacheComponent.BDD_ATTRIBUTES), {'bdd_attributes': BDD_Attributes_jsoned})
    else:
        BDD_attributes = cache.get_value(getCacheName(corpus_id, chosen_document_name, CacheComponent.BDD_ATTRIBUTES), 'bdd_attributes')
        BDD_Attributes = [BDDAttribute.fromJSON(attribute) for attribute in BDD_attributes]
        relationshipParser.bdd_attributes = BDD_Attributes

    if not bdd_plot_chosen_word:
        bdd_plot_chosen_word = "engine"

    bddAugmenter = BDDAugmenter(
        relationshipMapper.typed_relationships,
        noun_tf_idf_scores=key_nouns,
        noun_wordnet_scores=relationshipParser.wordnet_depth_memo,
        bdd_attributes=relationshipParser.bdd_attributes,
        bdd_plot_word=bdd_plot_chosen_word,
        bdd_plot_path=f"{chosen_document_name_without_ext}_{bdd_plot_chosen_word}_with_attributes_bdd.png"
    )
    block_dict = bddAugmenter.bdd_graph.block_dict
    block_dict = {block_name: block.toJSON() for block_name, block in block_dict.items()}
    
    cache.set(getCacheName(corpus_id, chosen_document_name, CacheComponent.BDD_BLOCK_DICT), {'bdd_block_dict': block_dict})

def from_cache_to_code_gen(corpus_id, chosen_document_path):
    chosen_document_name = os.path.basename(chosen_document_path)
    block_dict = cache.get_value(getCacheName(corpus_id, chosen_document_name, CacheComponent.BDD_BLOCK_DICT), 'bdd_block_dict')
    block_dict = {block_name: BDDBlock.fromJSON(block) for block_name, block in block_dict.items()}
    print(block_dict)
    target_dir = Path(__file__).resolve().parent / 'codegen'
    system_name = corpus_id + chosen_document_name.split('.')[0]
    filegen = FileGenerator(block_dict, target_dir, system_name)


if __name__ == "__main__":
    cache = Cache(CACHE_DIR)

    # FlyingMAchine
    # corpus_id = "FlyingMachines"
    # corpus_dir_id = "chapters"
    # chosen_document_path = Path(__file__).resolve().parent / 'Assets' / corpus_id / "resolved_chapters" / "chapter_16_resolved.txt"
    # chosen_document_name = os.path.basename(chosen_document_path)
    # bdd_plot_chosen_word = "glider"
    # # export_key_phrase_path = Path(__file__).resolve().parent / 'Assets' / corpus_id / "dynamo_test" / f"key_phrase_coref_{chosen_document_name}"
    # export_key_phrase_path = None

    # Patents
    corpus_id = "Patents"
    corpus_dir_id = "txt"
    chosen_document_path = Path(__file__).resolve().parent / 'Assets' / corpus_id / "txt" / "JP6875871B2.txt"
    chosen_document_name = os.path.basename(chosen_document_path)
    bdd_plot_chosen_word = "turbine"
    export_key_phrase_path = None

    main_loop_to_rel_extraction(corpus_id=corpus_id, corpus_dir_id=corpus_dir_id,document_path=chosen_document_path)
    from_cache_to_Bdd_Diagram(corpus_id=corpus_id,
                              corpus_dir_id=corpus_dir_id,
                              chosen_document_path=chosen_document_path,
                              chosen_document_name=chosen_document_name,
                              bdd_plot_chosen_word=bdd_plot_chosen_word,
                              export_key_phrase_path=export_key_phrase_path)
    from_cache_to_code_gen(corpus_id, chosen_document_path)
    pass