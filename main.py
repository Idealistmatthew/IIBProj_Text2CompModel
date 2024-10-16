from artificer.util.chapter_split import split_chapters
import os

ASSET_DIR = './Assets'


if __name__ == "__main__":

    # Only run this script if it is a new document to partition

    book_dir = os.path.join(ASSET_DIR, 'FlyingMachines')
    epub_dir = os.path.join(book_dir, 'flying_machines.epub')
    split_chapters(book_dir, epub_dir)

    pass