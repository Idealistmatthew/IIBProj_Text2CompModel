import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os
import re

def split_chapters(book_dir: str, epub_dir: str):
    """Split an EPUB file into separate text files for each chapter."""

    # Load corpus
    book = epub.read_epub(epub_dir)
    print(book)

    # Output Directory for chapter text files
    output_dir = os.path.join(book_dir, 'chapters')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    chapter_counter = 1

    # Function to split by heading tags
    def split_by_heading(soup):
        """Split content by <h1>, <h2>, or <h3> tags, which usually represent chapters or sections."""
        chapters = []
        current_chapter = []

        for tag in soup.find_all(True):
            if tag.name in ['h1', 'h2', 'h3']:
                if current_chapter:
                    chapters.append("\n".join(current_chapter))
                    current_chapter = []
                current_chapter.append(tag.get_text().strip())  # Add the chapter title
            else:
                current_chapter.append(tag.get_text().strip())
        
        if current_chapter:
            chapters.append("\n".join(current_chapter))
        
        return chapters

    # Extract and save each chapter as a separate text file
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')

            # Split content into chapters based on heading tags
            chapters = split_by_heading(soup)
                
            for chapter in chapters:
                chapter_text = chapter.strip()
                if chapter_text:
                    # Save each chapter as a separate text file
                    with open(f'{output_dir}/chapter_{chapter_counter}.txt', 'w', encoding='utf-8') as f:
                        f.write(chapter_text)
                    print(f'Chapter {chapter_counter} saved.')
                    chapter_counter += 1

    print('All chapters extracted and saved!')

def extract_chapters(chapter_dir):
    """Extract chapters from text files in a directory."""
    chapters = []
    chapter_file_pattern = r'^chapter_\d+\.txt$'
    for file in os.listdir(chapter_dir):
        if re.match(chapter_file_pattern, os.path.basename(file)):
            with open(os.path.join(chapter_dir, file), 'r', encoding='utf-8') as f:
                chapter_text = f.read()
                chapters.append(chapter_text)
    return chapters