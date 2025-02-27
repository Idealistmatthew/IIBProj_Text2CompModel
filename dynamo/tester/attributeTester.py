from dynamo.sysMLAugmenter.types import BDDBlock, BDDAttribute
import spacy

SIMILARITY_TRESHOLD = 0.7

class ComparisonResults():
    def __init__(self, normalised_matches: float, normalised_similarity: float):
        self.normalised_matches = normalised_matches
        self.normalised_similarity = normalised_similarity

    def __repr__(self):
        return f"Normalised Matches: {self.normalised_matches}, Normalised Similarity: {self.normalised_similarity}"

class AttributeTester():

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def compare_block_dict(self, block_dict_1: dict[str, BDDBlock], block_dict_2: dict[str, BDDBlock]) -> float:
        """
        If block_dict_1 is the test_data and block_dict_2 is the model answer, this will return the recall,
        and the precision can be calculated by swapping the arguments.
        """
        total_similarity = 0
        matches = 0
        for block_id in block_dict_1.keys():
            if block_id in block_dict_2.keys():
                total_similarity += self.compare_attributes(block_dict_1[block_id], block_dict_2[block_id])
                matches += 1
        normalised_matches = matches / len(block_dict_1)
        normalised_similarity = total_similarity / len(block_dict_1)
        return ComparisonResults(normalised_matches, normalised_similarity)

    def compare_block_dict_nonexact(self, block_dict_1: dict[str, BDDBlock], block_dict_2: dict[str, BDDBlock]) -> float:
        """
        If block_dict_1 is the test_data and block_dict_2 is the model answer, this will return the recall,
        and the precision can be calculated by swapping the arguments.
        """
        total_similarity = 0
        total_matches = 0
        for block_id in block_dict_1.keys():
            nlp_1 = self.nlp(block_id)
            current_similarity = 0
            for block_id_2 in block_dict_2.keys():
                nlp_2 = self.nlp(block_id_2)
                sim = nlp_1.similarity(nlp_2)
                if sim > SIMILARITY_TRESHOLD:
                    current_similarity = max(current_similarity, self.compare_attributes(block_dict_1[block_id], block_dict_2[block_id_2]))
            if current_similarity > 0:
                total_matches += 1
            total_similarity += current_similarity
        normalised_matches = total_matches / len(block_dict_1)
        normalised_similarity = total_similarity / len(block_dict_1)
        return ComparisonResults(normalised_matches, normalised_similarity)

    def compare_attributes(self, block_1 : BDDBlock, block_2: BDDBlock) -> float:
        total_similarity = 0
        if len(block_1.attributes) == 0:
            return 1
        if len(block_2.attributes) == 0:
            return 0
        for attribute in block_1.attributes:
            curr_similarity = 0
            for attribute_2 in block_2.attributes:
                cat_1 = self.nlp(attribute.category)
                cat_2 = self.nlp(attribute_2.category)
                sim_cat = cat_1.similarity(cat_2)
                if sim_cat > SIMILARITY_TRESHOLD:
                    if str(attribute.value).isnumeric() and str(attribute_2.value).isnumeric():
                        if attribute.value == attribute_2.value:
                            if attribute.unit and attribute.unit == attribute_2.unit:
                                curr_similarity = 1
                    if not str(attribute.value).isnumeric() and not str(attribute_2.value).isnumeric():
                        val_1 = self.nlp(attribute.value)
                        val_2 = self.nlp(attribute_2.value)
                        sim_val = val_1.similarity(val_2)
                        curr_similarity = max(curr_similarity, sim_val)
            total_similarity += curr_similarity
        normalised_similarity = total_similarity / len(block_1.attributes)
        return normalised_similarity
                    