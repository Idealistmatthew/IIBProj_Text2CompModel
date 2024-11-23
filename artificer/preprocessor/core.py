from typing import Any
import nltk
from artificer.util.chapter_split import extract_documents
from pathlib import Path

class Preprocessor:
    """Preprocessor class for preprocessing the data."""
    def __init__(self, documents_dir: str):
        """
        Inputs
        -------
        chapters_dir: str
            The directory containing the chapters of the corpus

        Returns
        -------
        None
        """
        self.chapters_dir: str = documents_dir
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        if documents_dir:
            extracted_documents = extract_documents(documents_dir)
            self.documents: list[str] = extracted_documents[0]
            self.document_dict: dict[str, int] = extracted_documents[1]

        self.stop_words = set(nltk.corpus.stopwords.words('english')) 

        self.tokenized_documents: list[list[str]] = [[]]
        self.sentence_tokenized_documents: list[list[str]] = [[]]
        self.filtered_document_tokens: list[list[str]] = [[]]
        self.pos_tagged_documents: list[list[tuple[str, str]] | list] = [[]]
        self.named_entities: list[nltk.Tree] = []
        self.nouns: list[list[str]] = [[]]
    
    def preprocess(self):
        """Preprocess the chapters."""
        self.tokenize_documents()
        self.sentence_tokenize_documents()
        self.filter_tokens()
        self.pos_tag_documents()
        self.noun_extraction()
        return None

    def get_chapter_dict(self) -> dict[str, int]:
        """Return the dictionary of chapters."""
        return self.document_dict

    
    def tokenize_documents(self) -> list[list[str]]:
        """Perform word tokenization on the chapters."""
        tokenized_documents = [nltk.word_tokenize(chapter) for chapter in self.documents]
        print("[STATUS] Tokenization complete")
        self.tokenized_documents = tokenized_documents
        return tokenized_documents
    
    def sentence_tokenize_documents(self) -> list[list[str]]:
        """Perform sentence tokenization on the chapters."""
        sentence_tokenized_chapters = [nltk.sent_tokenize(chapter) for chapter in self.documents]
        print("[STATUS] Sentence tokenization complete")
        self.sentence_tokenized_documents = sentence_tokenized_chapters
        return sentence_tokenized_chapters

    def filter_tokens(self) -> list[list[str]]:
        """Reomve stop words and lemmatiize the tokens."""
        filtered_document_tokens = []
        for tokenized_chapter in self.tokenized_documents:
            filtered_chapter = [self.lemmatizer.lemmatize(token.lower()) for token in tokenized_chapter if token.lower() not in self.stop_words]
            filtered_document_tokens.append(filtered_chapter)
        self.filtered_document_tokens = filtered_document_tokens
        print("[STATUS] Filtering complete")
        return filtered_document_tokens
    
    def process_phrase(self, phrase: str) -> list[str]:
        """Process a phrase."""
        tokens = nltk.word_tokenize(phrase)
        filtered_tokens = [self.lemmatizer.lemmatize(token.lower()) for token in tokens if token.lower() not in self.stop_words]
        pos_tagged_tokens = nltk.pos_tag(filtered_tokens)
        noun_tokens = [word for word, tag in pos_tagged_tokens if tag in ['NN', 'NNS', 'NNP', 'NNPS']]
        return noun_tokens
    
    def pos_tag_documents(self) -> list[list[tuple[str, str]] | list]:
        """Perform POS tagging on the chapters."""
        pos_tagged_chapters = [nltk.pos_tag(chapter) for chapter in self.filtered_document_tokens]
        self.pos_tagged_documents = pos_tagged_chapters
        print("[STATUS] POS tagging complete")
        return pos_tagged_chapters
    
    def named_entity_recognition(self) -> list[nltk.Tree]:
        """Perform named entity recognition on the chapters."""
        named_entities = []
        for chapter in self.pos_tagged_documents:
            named_entities.append(nltk.ne_chunk(chapter))
        self.named_entities = named_entities
        print("[STATUS] Named entity recognition complete")
        return named_entities
    
    def noun_extraction(self):
        """Extract nouns from the chapters."""
        self.nouns = [[word for word, tag in chapter if tag in ['NN', 'NNS', 'NNP', 'NNPS']] for chapter in self.pos_tagged_documents]
        return self.nouns

