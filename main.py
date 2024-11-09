from artificer.util.chapter_split import split_chapters
import os

from artificer.cache.core import Cache

from pathlib import Path
from artificer.preprocessor.core import Preprocessor
from artificer.keyNounExtractor.core import KeyNounExtractor
from artificer.relationshipExtractor.core import RelationshipExtractor, RelationshipParser, RelationshipSerialiser
from artificer.relationshipExtractor.mapper import RelationshipMapper
from artificer.sysMLAugmenter.bddAug import BDDAugmenter

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

def try_cache(cache_name, dict, cache_dir='jsoncaches'):
    cache = Cache(cache_dir)
    cache.set(cache_name, dict)
    print(cache.get_cache(cache_name))
    cache.add(cache_name, {"new_value": 10})
    print(cache.get_cache(cache_name))
    cache.delete_cache_entry(cache_name, 'old_value')
    print(cache.get_cache(cache_name))
    print(cache.get_value(cache_name, 'new_value'))
    return None

def main_loop():
    cache = Cache(CACHE_DIR)
    chapters_dir =  Path(__file__).resolve().parent / 'Assets' / 'FlyingMachines' / 'chapters'
    preprocessor = Preprocessor(chapters_dir=chapters_dir)
    preprocessor.preprocess()
    chapter_num_dict = preprocessor.get_chapter_dict()

    cache.set('sentence_tokenized_chapters', {'sentence_tokenized_chapters': preprocessor.sentence_tokenized_chapters})

    print(preprocessor.nouns)
    cache.set('preprocessed_nouns', {'nouns': preprocessor.nouns})
    print(cache.get_cache('preprocessed_nouns'))

    # print(chapter_num_dict)

    chosen_chapter_name = "chapter_38.txt"
    chosen_chapter_num = chapter_num_dict[chosen_chapter_name]

    # print(preprocessor.nouns)
    # print(len(preprocessor.nouns))

    key_noun_extractor = KeyNounExtractor(
        cache.get_value(PREPROCESSED_NOUNS_CACHE, 'nouns' ),
                                           chosen_chapter=chosen_chapter_num,
                                           tf_idf_limit=HYPERPARAMS['tf_idf'])
    cache.set(f"Flying_Machines_{chosen_chapter_name}_key_nouns", {'tf_idf': key_noun_extractor.chosen_chapter_tf_idf
                                                                   ,'key_nouns': key_noun_extractor.key_nouns})

    # relationshipExtractor = RelationshipExtractor(tokenized_sentences = cache.get_value('sentence_tokenized_chapters', 'sentence_tokenized_chapters'), chosen_chapter=chosen_chapter_num)
    # cache.set(f"Flying_Machines_{chosen_chapter_name}_raw_relationships", 
    #           {'relationships': relationshipExtractor.extracted_relationships})

if __name__ == "__main__":
    cache = Cache(CACHE_DIR)
    # main_loop()

    # Only run this script if it is a new document to partition

    # book_dir = os.path.join(ASSET_DIR, 'FlyingMachines')
    # epub_dir = os.path.join(book_dir, 'flying_machines.epub')
    # split_chapters(book_dir, epub_dir)

    # relationshipExtractor = RelationshipExtractor(tokenized_sentences = cache.get_value('sentence_tokenized_chapters', 'sentence_tokenized_chapters'), chosen_chapter=4)
    # cache.set('Flying_Machines_Chapter4_relationships', {'relationships': relationshipExtractor.extraced_relationships})


    chapters_dir =  Path(__file__).resolve().parent / 'Assets' / 'FlyingMachines' / 'chapters'
    preprocessor = Preprocessor(chapters_dir=chapters_dir)
    chapter_num_dict = preprocessor.get_chapter_dict()
    chosen_chapter_name = "chapter_38.txt"
    chosen_chapter_num = chapter_num_dict[chosen_chapter_name]
    relationships = cache.get_value(f"Flying_Machines_{chosen_chapter_name}_raw_relationships", 'relationships')

    key_nouns: dict[str, float] = cache.get_value(f"Flying_Machines_{chosen_chapter_name}_key_nouns", 'key_nouns')

    relationshipParser = RelationshipParser(
        relationships, preprocessor,key_nouns, phrase_length_limit=HYPERPARAMS['phrase_length']
        , key_phrase_metric_tresh=HYPERPARAMS['key_phrase_selection'])
    relationshipMapper = RelationshipMapper(relationshipParser.filtered_relationships)

    
    

    bddAugmenter = BDDAugmenter(relationshipMapper.typed_relationships,
                                noun_tf_idf_scores=key_nouns,
                                noun_wordnet_scores=relationshipParser.wordnet_depth_memo)


    # serialisable_relationships = [RelationshipSerialiser.toDict(relationship) for relationship in relationshipParser.processed_relationships]
    # cache.set(f"Flying_Machines_{chosen_chapter_name}_processed_relationships", {'processed_relationships': serialisable_relationships})
    # export_key_phrase_path = Path(chapters_dir).parent / "artificer_test" / f"key_phrase_{chosen_chapter_name}"
    # relationshipParser.export_key_phrases(export_key_phrase_path)


    pass