from dynamo.sysMLAugmenter.types import BDDBlock, BDDAttribute
import spacy

SIMILARITY_TRESHOLD = 0.7

class ComparisonResults():
    def __init__(self, normalised_matches: float, normalised_similarity: float, match_dict: dict[tuple[str, str], float]):
        self.normalised_matches = normalised_matches
        self.normalised_similarity = normalised_similarity
        self.match_dict = match_dict

    def __repr__(self):
        table = "Comparison Results:\n"
        table += f"{'Block Pair':<30} {'Similarity':<10}\n"
        table += "-" * 40 + "\n"
        for (block_1, block_2), similarity in self.match_dict.items():
            table += f"{block_1 + ' - ' + block_2:<30} {similarity:<10.2f}\n"
        table += "-" * 40 + "\n"
        table += f"{'Normalised Matches':<30} {self.normalised_matches:<10.2f}\n"
        table += f"{'Normalised Similarity':<30} {self.normalised_similarity:<10.2f}\n"
        return table

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
        match_dict = {}
        for block_id in block_dict_1.keys():
            if block_id in block_dict_2.keys():
                curr_similarity = self.compare_attributes(block_dict_1[block_id], block_dict_2[block_id])
                total_similarity += curr_similarity
                matches += 1
                match_dict[(block_id, block_id)] = curr_similarity
        normalised_matches = matches / len(block_dict_1)
        normalised_similarity = total_similarity / len(block_dict_1)
        return ComparisonResults(normalised_matches, normalised_similarity, match_dict)

    def compare_block_dict_nonexact(self, block_dict_1: dict[str, BDDBlock], block_dict_2: dict[str, BDDBlock]) -> float:
        """
        If block_dict_1 is the test_data and block_dict_2 is the model answer, this will return the recall,
        and the precision can be calculated by swapping the arguments.
        """
        total_similarity = 0
        total_matches = 0
        match_dict = {}
        for block_id in block_dict_1.keys():
            has_match = False
            if block_id in block_dict_2.keys():
                current_similarity = self.compare_attributes(block_dict_1[block_id], block_dict_2[block_id])
                total_similarity += current_similarity
                has_match = True
                current_second_block = block_id
            else:
                nlp_1 = self.nlp(block_id)
                current_similarity = 0
                current_second_block = None
                category_match = 0
                for block_id_2 in block_dict_2.keys():
                    nlp_2 = self.nlp(block_id_2)
                    sim = nlp_1.similarity(nlp_2)
                    if sim > max(SIMILARITY_TRESHOLD, category_match):
                        has_match = True
                        current_similarity = self.compare_attributes(block_dict_1[block_id], block_dict_2[block_id_2])
                        current_second_block = block_id_2
            if has_match:
                total_matches += 1
                match_dict[(block_id, current_second_block)] = current_similarity
            total_similarity += current_similarity
        normalised_matches = total_matches / len(block_dict_1)
        normalised_similarity = total_similarity / len(block_dict_1)
        return ComparisonResults(normalised_matches, normalised_similarity, match_dict)

    def compare_attributes(self, block_1 : BDDBlock, block_2: BDDBlock) -> float:
        total_similarity = 0
        if len(block_1.attributes) == 0:
            return 1
        if len(block_2.attributes) == 0:
            return 0
        for attribute in block_1.attributes:
            curr_similarity = 0
            for attribute_2 in block_2.attributes:
                attr_1_cat = attribute.category.replace("_", " ").lower()
                attr_2_cat = attribute_2.category.replace("_", " ").lower()
                cat_1 = self.nlp(attr_1_cat)
                cat_2 = self.nlp(attr_2_cat)
                sim_cat = cat_1.similarity(cat_2)
                if sim_cat > SIMILARITY_TRESHOLD:
                    if str(attribute.value).isnumeric() and str(attribute_2.value).isnumeric():
                        value_similarity = self.nlp(str(attribute.value)).similarity(self.nlp(str(attribute_2.value)))
                        if attribute.unit:
                            unit_similarity = self.nlp(attribute.unit).similarity(self.nlp(attribute_2.unit))
                            curr_similarity = max(curr_similarity, value_similarity * 0.5 + unit_similarity * 0.5)
                        else:
                            curr_similarity = max(curr_similarity, value_similarity)
                    if not str(attribute.value).isnumeric() and not str(attribute_2.value).isnumeric():
                        val_1 = self.nlp(str(attribute.value))
                        val_2 = self.nlp(str(attribute_2.value))
                        sim_val = val_1.similarity(val_2)
                        curr_similarity = max(curr_similarity, sim_val)
            total_similarity += curr_similarity
        normalised_similarity = total_similarity / len(block_1.attributes)
        return normalised_similarity
                    