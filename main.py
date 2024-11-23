from artificer.util.chapter_split import split_chapters
import os

from artificer.cache.core import Cache

from pathlib import Path
from artificer.preprocessor.core import Preprocessor
from artificer.keyNounExtractor.core import KeyNounExtractor
from artificer.relationshipExtractor.core import RelationshipExtractor, RelationshipParser, RelationshipSerialiser
from artificer.relationshipExtractor.mapper import RelationshipMapper
from artificer.sysMLAugmenter.bddAug import BDDAugmenter

ASSET_DIR = './Assets'
CACHE_DIR = './jsoncaches'
PREPROCESSED_NOUNS_CACHE = 'preprocessed_nouns'

HYPERPARAMS = {
    'tf_idf': 0,
    'relationship': 0.5, # not using this yet since the relationships extracted at the moment are still manageable
    'phrase_length': 3,
    'key_phrase_selection': 0.6,
    'relationship_score_diff_tresh': 0.5
}

def main_loop_to_rel_extraction(corpus_id = None, document_dir_id = None, chosen_document_name = None): 
    cache = Cache(CACHE_DIR)
    if not corpus_id:
        corpus_id = "FlyingMachines"
    if not document_dir_id:
        document_dir_id = "chapters"
    documents_dir =  Path(__file__).resolve().parent / 'Assets' / corpus_id / document_dir_id
    preprocessor = Preprocessor(documents_dir=documents_dir)
    preprocessor.preprocess()
    chapter_num_dict = preprocessor.get_chapter_dict()

    if not chosen_document_name:
        chosen_document_name = "chapter_38.txt"
    chosen_document_num = chapter_num_dict[chosen_document_name]

    # print(preprocessor.nouns)
    # print(len(preprocessor.nouns))

    key_noun_extractor = KeyNounExtractor(
        preprocessor.nouns,
                                           chosen_chapter=chosen_document_num,
                                           tf_idf_limit=HYPERPARAMS['tf_idf'])
    cache.set(f"{corpus_id}_{chosen_document_name}_key_nouns", {'tf_idf': key_noun_extractor.chosen_chapter_tf_idf
                                                                   ,'key_nouns': key_noun_extractor.key_nouns})

    relationshipExtractor = RelationshipExtractor(tokenized_sentences = preprocessor.sentence_tokenized_documents, chosen_chapter=chosen_document_num)
    cache.set(f"{corpus_id}_{chosen_document_name}_raw_relationships", 
              {'relationships': relationshipExtractor.extracted_relationships})

    def new_partition(self):
        # Only run this script if it is a new document to partition

        book_dir = os.path.join(ASSET_DIR, 'FlyingMachines')
        epub_dir = os.path.join(book_dir, 'flying_machines.epub')
        split_chapters(book_dir, epub_dir)

def from_cache_to_Bdd_Diagram(corpus_id = None, document_dir_id = None, chosen_document_name = None, bdd_plot_chosen_word = None):
    if not corpus_id:
        corpus_id = "FlyingMachines"
    if not document_dir_id:
        document_dir_id = "chapters"
    documents_dir =  Path(__file__).resolve().parent / 'Assets' / corpus_id / document_dir_id
    preprocessor = Preprocessor(documents_dir=documents_dir)
    chapter_num_dict = preprocessor.get_chapter_dict()
    if not chosen_document_name:
        chosen_document_name = "chapter_38.txt"
    chosen_document_name_without_ext = chosen_document_name.split('.')[0]
    chosen_document_num = chapter_num_dict[chosen_document_name]
    relationships = cache.get_value(f"{corpus_id}_{chosen_document_name}_raw_relationships", 'relationships')

    key_nouns: dict[str, float] = cache.get_value(f"{corpus_id}_{chosen_document_name}_key_nouns", 'key_nouns')

    relationshipParser = RelationshipParser(
        relationships, preprocessor,key_nouns, phrase_length_limit=HYPERPARAMS['phrase_length']
        , key_phrase_metric_tresh=HYPERPARAMS['key_phrase_selection'],
        relationship_confidence_tresh=HYPERPARAMS['relationship'])
    relationshipMapper = RelationshipMapper(relationshipParser.filtered_relationships, relationship_score_diff_tresh=HYPERPARAMS['relationship_score_diff_tresh'])

    if not bdd_plot_chosen_word:
        bdd_plot_chosen_word = "bleriot"

    bddAugmenter = BDDAugmenter(relationshipMapper.typed_relationships,
                                noun_tf_idf_scores=key_nouns,
                                noun_wordnet_scores=relationshipParser.wordnet_depth_memo,
                                bdd_plot_word = bdd_plot_chosen_word,
                                bdd_plot_path= f"{chosen_document_name_without_ext}_{bdd_plot_chosen_word}_bdd.png")


    # serialisable_relationships = [RelationshipSerialiser.toDict(relationship) for relationship in relationshipParser.processed_relationships]
    # cache.set(f"{corpus_id}_{chosen_document_name}_processed_relationships", {'processed_relationships': serialisable_relationships})
    # export_key_phrase_path = Path(documents_dir).parent / "artificer_test" / f"key_phrase_{chosen_document_name}"
    # relationshipParser.export_key_phrases(export_key_phrase_path)


if __name__ == "__main__":
    cache = Cache(CACHE_DIR)

    # corpus_id = "ShaoHongAssets"
    # document_dir_id = "documents"
    # chosen_document_name = "Devices.txt"

    corpus_id = "FlyingMachines"
    document_dir_id = "chapters"
    chosen_document_name = "chapter_16.txt"

    # main_loop_to_rel_extraction(corpus_id=corpus_id, document_dir_id=document_dir_id, chosen_document_name=chosen_document_name)
    from_cache_to_Bdd_Diagram(corpus_id=corpus_id, document_dir_id=document_dir_id, chosen_document_name=chosen_document_name, bdd_plot_chosen_word="glider")
    pass