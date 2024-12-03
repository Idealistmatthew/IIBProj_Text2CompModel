from collections import Counter
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt

class KeyNounExtractor:
    """KeyNounExtractor class for extracting key nouns from the data."""
    def __init__(self, chapter_nouns: list[list[str]] ,chosen_chapter: int, tf_idf_limit: float):
        """
        Inputs
        -------
        chapter_nouns: list[list[str]]
            a list containing lists of nouns for each chapter, the first chapter is just the preface of the book
        chosen_chapter: int
            the index of the chapter to extract the key nouns (this index should be decremented by 1 to get the correct chapter)

        Returns
        -------
        None
        """
        self.chapter_nouns = chapter_nouns
        self.num_chapters = len(chapter_nouns)
        self.noun_counter: list[Counter] = [Counter(chapter) for chapter in self.chapter_nouns]
        self.document_frequency = self.calculate_document_frequency(self.noun_counter[chosen_chapter])
        self.chosen_chapter_tf_idf: dict[str, float] = self.calculate_tf_idf(self.noun_counter[chosen_chapter])
        # print(self.chosen_chapter_tf_idf)
        self.sorted_tf_idf = dict(sorted(self.chosen_chapter_tf_idf.items(), key=lambda item: item[1], reverse=True))
        max_tf_idf = max(self.sorted_tf_idf.values())
        self.sorted_tf_idf = {word: value / max_tf_idf for word, value in self.sorted_tf_idf.items()}
        self.key_nouns = {word: value for word, value in self.sorted_tf_idf.items() if value > tf_idf_limit}
        self.pretty_print_top_n(self.sorted_tf_idf, 30)
        self.show_word_cloud()
    
    def calculate_tf_idf(self, chapter_noun_counter: Counter) -> dict[str, float]:
        """Calculate the TF-IDF for the chosen chapter."""
        tf_idf = {}
        for word in chapter_noun_counter:
            tf = np.log(chapter_noun_counter[word] +1)
            idf = np.log(self.num_chapters/(self.document_frequency[word] + 1)) + 1
            tf_idf[word] = tf * idf
        return tf_idf
    
    def pretty_print_top_n(self, data: dict[str, float], n: int):
        """Pretty print the top n entries of a dictionary."""
        for i, (key, value) in enumerate(data.items()):
            if i >= n:
                break
            print(f"{key}: {value:.4f}")
    
    def calculate_document_frequency(self, chapter_noun_counter: Counter) -> dict[str, int]:
        """Calculate the document frequency for the chosen chapter."""
        document_frequency = {}
        for word in chapter_noun_counter:
            document_frequency[word] = sum([1 for chapter in self.chapter_nouns if word in chapter])
        return document_frequency

    def show_word_cloud(self):
        wordcloud = WordCloud(width = 800, height = 800, background_color=None, mode="RGBA").generate_from_frequencies(self.chosen_chapter_tf_idf)

        # Display the generated word cloud using matplotlib
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')  # Hide the axes
        plt.show()