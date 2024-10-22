from artificer.util.chapter_split import split_chapters
import os

from pathlib import Path
from artificer.preprocessor.core import Preprocessor
from artificer.keyNounExtractor.core import KeyNounExtractor

ASSET_DIR = './Assets'


if __name__ == "__main__":

    # Only run this script if it is a new document to partition

    # book_dir = os.path.join(ASSET_DIR, 'FlyingMachines')
    # epub_dir = os.path.join(book_dir, 'flying_machines.epub')
    # split_chapters(book_dir, epub_dir)

    chapters_dir =  Path(__file__).resolve().parent / 'Assets' / 'FlyingMachines' / 'chapters'
    preprocessor = Preprocessor(chapters_dir=chapters_dir)
    key_noun_extractor = KeyNounExtractor(preprocessor.nouns, chosen_chapter=4)


    pass