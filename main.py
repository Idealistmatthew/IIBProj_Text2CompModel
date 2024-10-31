from artificer.util.chapter_split import split_chapters
import os

from artificer.cache.core import Cache

from pathlib import Path
from artificer.preprocessor.core import Preprocessor
from artificer.keyNounExtractor.core import KeyNounExtractor
from artificer.relationshipExtractor.core import RelationshipExtractor, RelationshipParser

ASSET_DIR = './Assets'
CACHE_DIR = './jsoncaches'
PREPROCESSED_NOUNS_CACHE = 'preprocessed_nouns'

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


if __name__ == "__main__":
    cache = Cache(CACHE_DIR)

    # Only run this script if it is a new document to partition

    # book_dir = os.path.join(ASSET_DIR, 'FlyingMachines')
    # epub_dir = os.path.join(book_dir, 'flying_machines.epub')
    # split_chapters(book_dir, epub_dir)

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

    key_noun_extractor = KeyNounExtractor(cache.get_value(PREPROCESSED_NOUNS_CACHE, 'nouns' ), chosen_chapter=chosen_chapter_num)
    cache.set(f"Flying_Machines_{chosen_chapter_name}_key_nouns", {'tf_idf': key_noun_extractor.chosen_chapter_tf_idf})

    

    # try_cache('test_cache', {'value': 5, 'old_value': 10})

    # relationshipExtractor = RelationshipExtractor(tokenized_sentences = cache.get_value('sentence_tokenized_chapters', 'sentence_tokenized_chapters'), chosen_chapter=4)
    # cache.set('Flying_Machines_Chapter4_relationships', {'relationships': relationshipExtractor.extraced_relationships})

    # relationships = cache.get_value('Flying_Machines_Chapter4_relationships', 'relationships')
    # # print(relationships)
    # print("Type",type(relationships))
    # relationshipParser = RelationshipParser(relationships)
    # cache.set('Flying_Machines_Chapter4_parsed_relationships', {'parsed_relationships': relationshipParser.parsed_relationships})


    pass