from pathlib import Path
from dynamo.preprocessor.core import Preprocessor

class KeyPhraseTester:
    def __init__(self, corpus_dir: str, ground_truth_path: str, test_phrase_path: str):
        """
        Inputs
        -------
        corpus_dir: str
            The directory containing the corpus

        Returns
        -------
        None
        """
        self.corpus_dir: str = corpus_dir
        self.ground_truth_path: str = ground_truth_path
        self.test_phrase_path: str = test_phrase_path
        self.preprocessor: Preprocessor = Preprocessor(corpus_dir=None)

        self.ground_truth_phrases: list[str] = self.extract_and_process_phrases(ground_truth_path)
        self.test_phrases: list[str] = self.extract_and_process_phrases(test_phrase_path)

        self.exact_match_precision, self.exact_match_recall = self.exact_match_test()

        self.ground_truth_phrases = self.split_phrases(self.ground_truth_phrases)
        self.test_phrases = self.split_phrases(self.test_phrases)

        self.fuzzy_match_precision, self.fuzzy_match_recall = self.fuzzy_match_test()


        self.print_results()

    def extract_and_process_phrases(self, phrase_txt_path: str):
        """Extract and process the key phrases from the text file."""
        with open(phrase_txt_path, 'r') as file:
            phrases = [line.strip() for line in file]
            phrases = [" ".join(self.preprocessor.noun_extract_phrase(phrase)) for phrase in phrases if phrase != '']
            phrases = list(set(phrases))
        return phrases
    
    def exact_match_test(self):
        """Perform an exact match test between the ground truth and the test phrases."""

        matched_phrase_num = 0
        matched_phrases = []
        for phrase in self.test_phrases:
            if phrase in self.ground_truth_phrases:
                matched_phrase_num += 1
                matched_phrases.append(phrase)
        
        print("Matched Phrases: ", matched_phrases)
        exact_match_precision = matched_phrase_num / len(self.test_phrases)
        exact_match_recall = matched_phrase_num / len(self.ground_truth_phrases)
        return exact_match_precision, exact_match_recall
    
    def split_phrases(self, phrases: list[str]):
        """Convert the list of phrase to a list of list list of words."""
        return [phrase.split() for phrase in phrases]

    def fuzzy_match_test(self):
        """Perform a fuzzy match test between the ground truth and the test phrases."""
        
        #Precision Test
        matched_test_phrase = 0
        for test_phrase in self.test_phrases:
            if any(self.fuzzy_match(test_phrase, phrase) for phrase in self.ground_truth_phrases):
                matched_test_phrase += 1
        fuzzy_match_precision = matched_test_phrase / len(self.test_phrases)

        #Recall Test
        matched_ground_truth_phrase = 0

        unfuzzy_matched_ground_truth_phrases = []
        for ground_truth_phrase in self.ground_truth_phrases:
            if any(self.fuzzy_match(ground_truth_phrase, phrase) for phrase in self.test_phrases):
                matched_ground_truth_phrase += 1
            else:
                unfuzzy_matched_ground_truth_phrases.append(ground_truth_phrase)

        print("Unfuzzy Matched Phrases: ", unfuzzy_matched_ground_truth_phrases)
        
        fuzzy_match_recall = matched_ground_truth_phrase / len(self.ground_truth_phrases)
        return fuzzy_match_precision, fuzzy_match_recall

    def fuzzy_match(self, phrase1: list[str], phrase2: list[str]):
        """Perform a fuzzy match between two phrases."""
        return any(word in phrase2 for word in phrase1)


    def print_results(self):
        """Print the results of the test."""
        print(f"File tested: {self.test_phrase_path}")
        print(f"Ground Truth file: {self.ground_truth_path}")
        print(f"Number of Ground Truth Phrases: {len(self.ground_truth_phrases)}")
        print(f"Number of Test Phrases: {len(self.test_phrases)}")
        print(f"Exact Match Precision: {self.exact_match_precision}")
        print(f"Exact Match Recall: {self.exact_match_recall}")
        print(f"Fuzzy Match Precision: {self.fuzzy_match_precision}")
        print(f"Fuzzy Match Recall: {self.fuzzy_match_recall}")


                

if __name__ == "__main__":
    corpus_dir = Path(__file__).resolve().parent.parent.parent / 'Assets' / 'FlyingMachines'
    ground_truth_path = Path(__file__).resolve().parent.parent.parent / 'Assets' / 'FlyingMachines' / 'ground_truth' / 'key_phrase_chapter_38.txt'
    gpt_test_phrase_path = Path(__file__).resolve().parent.parent.parent / 'Assets' / 'FlyingMachines' / 'GPT_test' / 'key_phrase_chapter_38.txt'

    artificer_test_phrase_path = Path(__file__).resolve().parent.parent.parent / 'Assets' / 'FlyingMachines' / 'artificer_test' / 'key_phrase_chapter_38.txt'

    gptKeyPhraseTester = KeyPhraseTester(corpus_dir, ground_truth_path, gpt_test_phrase_path)
    artificerKeyPhraseTester = KeyPhraseTester(corpus_dir, ground_truth_path, artificer_test_phrase_path)