from enum import Enum

class CacheComponent(Enum):
    RAW_RELATIONSHIPS = 1
    KEY_NOUNS = 2
    BDD_ATTRIBUTES = 3
    BDD_BLOCK_DICT = 4
    TOKENIZED_SENTENCES = 5

def getCacheComponentName(component: CacheComponent):
    if component == CacheComponent.RAW_RELATIONSHIPS:
        return "raw_relationships"
    elif component == CacheComponent.KEY_NOUNS:
        return "key_nouns"
    elif component == CacheComponent.BDD_ATTRIBUTES:
        return "bdd_attributes"
    elif component == CacheComponent.BDD_BLOCK_DICT:
        return "bdd_block_dict"
    elif component == CacheComponent.TOKENIZED_SENTENCES:
        return "tokenized_sentences"
    else:
        return "UNKNOWN"

def getCacheName(corpus_id, chosen_document_name, component: CacheComponent):
    return f"{corpus_id}_{chosen_document_name}_{getCacheComponentName(component)}"
