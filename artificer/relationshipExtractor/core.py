from pyopenie import OpenIE5



class RelationshipExtractor:
    def __init__(self, tokenized_sentences: str, chosen_chapter: int):
        # Initialize any necessary variables or models here
        self.extractor = OpenIE5('http://localhost:8000')
        self.extraced_relationships = self.extract_relationships(tokenized_sentences[chosen_chapter])
        print(self.extraced_relationships)
    
    def extract_relationships(self, sentences: list[str]) -> list[str]:
        """Extract relationships from the given sentences."""
        relationships = []
        for sentence in sentences:
            relationships.append(self.extractor.extract(sentence))
        return relationships