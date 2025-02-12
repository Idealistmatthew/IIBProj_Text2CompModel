from dynamo.util.chapter_split import extract_document
from autocorrect import Speller

def auto_correct_doc(document_path,
                    resolved_path,
                      domain_specific_words: dict[str, int] = None):
    document = extract_document(document_path)

    spell = Speller()
    spell.nlp_data.update(domain_specific_words)

    resolved_text = spell(document)
    
    resolved_text_file = open(resolved_path, "w")
    resolved_text_file.write(resolved_text)

