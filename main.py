from artificer.util.chapter_split import split_chapters
import os

from artificer.cache.core import Cache

from pathlib import Path
from artificer.preprocessor.core import Preprocessor
from artificer.keyNounExtractor.core import KeyNounExtractor

ASSET_DIR = './Assets'

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

    # Only run this script if it is a new document to partition

    # book_dir = os.path.join(ASSET_DIR, 'FlyingMachines')
    # epub_dir = os.path.join(book_dir, 'flying_machines.epub')
    # split_chapters(book_dir, epub_dir)

    # chapters_dir =  Path(__file__).resolve().parent / 'Assets' / 'FlyingMachines' / 'chapters'
    # preprocessor = Preprocessor(chapters_dir=chapters_dir)
    # key_noun_extractor = KeyNounExtractor(preprocessor.nouns, chosen_chapter=4)

    try_cache('test_cache', {'value': 5, 'old_value': 10})


    pass