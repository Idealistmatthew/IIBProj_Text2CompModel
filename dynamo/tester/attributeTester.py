from dynamo.sysMLAugmenter.types import BDDBlock, BDDAttribute
import spacy

SIMILARITY_TRESHOLD = 0.7

class ComparisonResults():
    def __init__(self, normalised_matches: float, set_similarity: float, match_dict: dict[tuple[str, str], float],
                 zero_attribute_match_score: float = 1):
        self.normalised_matches = normalised_matches
        self.set_similarity = set_similarity
        self.match_dict = match_dict
        self.zero_attribute_match_score = zero_attribute_match_score

    def __repr__(self):
        table = "Comparison Results:\n"
        table += f"{'Block Pair':<30} {'Similarity':<10}\n"
        table += "-" * 40 + "\n"
        for (block_1, block_2), similarity in self.match_dict.items():
            table += f"{block_1 + ' - ' + block_2:<30} {similarity:<10.2f}\n"
        table += "-" * 40 + "\n"
        table += f"{'Normalised Matches':<30} {self.normalised_matches:<10.2f}\n"
        table += f"{'Set Similarity':<30} {self.set_similarity:<10.2f}\n"
        table += f"{'Zero Attribute Match Score':<30} {self.zero_attribute_match_score:<10.2f}\n"
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

    def compare_block_dict_nonexact(self, ground_truth_block_dict: dict[str, BDDBlock], extracted_block_dict: dict[str, BDDBlock]) -> float:
        """
        This will return the recall, and the precision can be calculated by swapping the arguments.
        """
        total_similarity = 0
        total_matches = 0
        match_dict = {}
        num_both_block_no_attributes = 0
        num_ground_truth_block_noattr_extracted_yes_attributes = 0
        num_extracted_block_no_attributes = 0

        num_no_match_for_block = 0
        num_ground_truth_noattr = 0

        for block_id in extracted_block_dict.keys():
            if len(extracted_block_dict[block_id].attributes) == 0:
                num_extracted_block_no_attributes += 1

        for block_id in ground_truth_block_dict.keys():
            has_match = False
            if len(ground_truth_block_dict[block_id].attributes) == 0:
                num_ground_truth_noattr += 1
            if block_id in extracted_block_dict.keys():
                if len(ground_truth_block_dict[block_id].attributes) == 0 and len(extracted_block_dict[block_id].attributes) == 0:
                    num_both_block_no_attributes += 1
                elif len(ground_truth_block_dict[block_id].attributes) == 0 and len(extracted_block_dict[block_id].attributes) != 0:
                    num_ground_truth_block_noattr_extracted_yes_attributes += 1
                else:
                    current_similarity = self.compare_attributes(ground_truth_block_dict[block_id], extracted_block_dict[block_id])
                    # total_similarity += current_similarity
                    has_match = True
                    current_second_block = block_id
            else:
                nlp_ground_truth = self.nlp(block_id)
                current_similarity = 0
                current_second_block = None
                category_match = 0
                add_both_no_attributes = False
                add_ground_truth_noattr_extracted_yes_attributes = False
                for extracted_block_id in extracted_block_dict.keys():
                    no_match_for_block = True
                    nlp_cand_extracted = self.nlp(extracted_block_id)
                    sim = nlp_ground_truth.similarity(nlp_cand_extracted)
                    if sim > max(SIMILARITY_TRESHOLD, category_match):
                        no_match_for_block = False
                        if len(ground_truth_block_dict[block_id].attributes) == 0 and len(extracted_block_dict[extracted_block_id].attributes) == 0:
                            has_match = False
                            add_both_no_attributes = True
                            # print(f"Both blocks have no attributes: {block_id} - {block_id_2}")#
                        elif len(ground_truth_block_dict[block_id].attributes) == 0 and len(extracted_block_dict[extracted_block_id].attributes) != 0:
                            has_match = False
                            add_ground_truth_noattr_extracted_yes_attributes = True
                            # print(f"Extracted block has no attributes, ground truth block has attributes: {block_id} - {block_id_2}")
                        else:
                            add_both_no_attributes = False
                            add_ground_truth_noattr_extracted_yes_attributes = False
                            has_match = True
                            current_similarity = self.compare_attributes(ground_truth_block_dict[block_id], extracted_block_dict[extracted_block_id])
                            current_second_block = extracted_block_id
                if add_ground_truth_noattr_extracted_yes_attributes:
                    num_ground_truth_block_noattr_extracted_yes_attributes += 1
                if add_both_no_attributes:
                    num_both_block_no_attributes += 1
                if no_match_for_block:
                    num_no_match_for_block += 1
                
            if has_match:
                total_matches += 1
                match_dict[(block_id, current_second_block)] = current_similarity
                total_similarity += current_similarity
        
        normalised_matches = (len(ground_truth_block_dict) - num_no_match_for_block) / len(ground_truth_block_dict)
        if num_ground_truth_block_noattr_extracted_yes_attributes + num_both_block_no_attributes > 0:
            print(f"num_both_block_no_attributes: {num_both_block_no_attributes}, num_ground_truth_block_noattr_extracted_yes_attributes: {num_ground_truth_block_noattr_extracted_yes_attributes}")
            if num_ground_truth_noattr == 0:
                zero_attribute_match_score = 1
            else:
                zero_attribute_match_score = num_both_block_no_attributes / (num_both_block_no_attributes + num_ground_truth_block_noattr_extracted_yes_attributes)
        else:
            zero_attribute_match_score = 1
        print(f"total_similarity: {total_similarity}, len(block_dict_1): {len(ground_truth_block_dict)}, num_extracted_block_no_attributes: {num_extracted_block_no_attributes}")
        set_similarity = total_similarity / (len(ground_truth_block_dict) - num_ground_truth_noattr)
        return ComparisonResults(normalised_matches, set_similarity, match_dict, zero_attribute_match_score)

    def compare_attributes(self, ground_truth_block : BDDBlock, extracted_block: BDDBlock) -> float:
        total_similarity = 0
        if len(ground_truth_block.attributes) == 0:
            return 1
        if len(extracted_block.attributes) == 0:
            return 0
        for attribute in ground_truth_block.attributes:
            curr_similarity = 0
            for attribute_2 in extracted_block.attributes:
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
        normalised_similarity = total_similarity / len(ground_truth_block.attributes)
        return normalised_similarity
                    