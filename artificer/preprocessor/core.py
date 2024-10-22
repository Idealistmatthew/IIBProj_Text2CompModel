from typing import Any
import nltk
from artificer.util.chapter_split import extract_chapters
from pathlib import Path

class Preprocessor:
    """Preprocessor class for preprocessing the data."""
    def __init__(self, chapters_dir: str):
        """
        Inputs
        -------
        chapters_dir: str
            The directory containing the chapters of the corpus

        Returns
        -------
        None
        """
        self.chapters_dir: str = chapters_dir
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.chapters: list = extract_chapters(chapters_dir)

        # The following assignments hold a lot of intermediate data, we should remove this if memory becomes an issue and it isn't used elsewhere
        self.tokenized_chapters: list[list[str]] = self.tokenize_chapters()
        print("[STATUS] Tokenization complete")
        self.filtered_chapter_tokens: list[list[str]] = self.filter_tokens()
        print("[STATUS] Filtering complete")
        self.pos_tagged_chapters: list[list[tuple[str, str]] | list] = self.pos_tag_chapters()
        print("[STATUS] POS tagging complete")
        self.named_entities: list[nltk.Tree] = self.named_entity_recognition()
        print("[STATUS] Named entity recognition complete")
        self.nouns: list[list[str]] = self.noun_extraction()
        print("[STATUS] Noun extraction complete") 

    
    def tokenize_chapters(self) -> list[list[str]]:
        """Perform word tokenization on the chapters."""
        tokenized_chapters = [nltk.word_tokenize(chapter) for chapter in self.chapters]
        return tokenized_chapters

    def filter_tokens(self) -> list[list[str]]:
        """Reomve stop words and lemmatiize the tokens."""
        stop_words = set(nltk.corpus.stopwords.words('english')) # Could be extracted into init if this is used again
        filtered_chapter_tokens = []
        for tokenized_chapter in self.tokenized_chapters:
            filtered_chapter = [self.lemmatizer.lemmatize(token.lower()) for token in tokenized_chapter if token.lower() not in stop_words]
            filtered_chapter_tokens.append(filtered_chapter)
        return filtered_chapter_tokens
    
    def pos_tag_chapters(self) -> list[list[tuple[str, str]] | list]:
        """Perform POS tagging on the chapters."""
        pos_tagged_chapters = [nltk.pos_tag(chapter) for chapter in self.filtered_chapter_tokens]
        return pos_tagged_chapters
    
    def named_entity_recognition(self) -> list[nltk.Tree]:
        """Perform named entity recognition on the chapters."""
        named_entities = []
        for chapter in self.pos_tagged_chapters:
            named_entities.append(nltk.ne_chunk(chapter))
        return named_entities
    
    def noun_extraction(self):
        """Extract nouns from the chapters."""
        return [[word for word, tag in chapter if tag in ['NN', 'NNS', 'NNP', 'NNPS']] for chapter in self.pos_tagged_chapters]
    


    


if __name__ == "__main__":
    # Load the chapters
    chapters_dir =  Path(__file__).resolve().parent.parent.parent / 'Assets' / 'FlyingMachines' / 'chapters'
    preprocessor = Preprocessor(chapters_dir=chapters_dir, chosen_chapter=4)
    
