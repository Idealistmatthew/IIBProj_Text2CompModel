from pathlib import Path
from dynamo.util.chapter_split import extract_corpus

import spacy

corpus_id = "FlyingMachines"
document_dir_id = "chapters"
corpus_dir = Path(__file__).resolve().parent.parent.parent / 'Assets' / corpus_id
documents_dir =  Path(__file__).resolve().parent.parent.parent / 'Assets' / corpus_id / document_dir_id

chosen_document_name = "chapter_16.txt"
chosen_doc_name_wo_ext = chosen_document_name.split(".")[0]

extracted_documents = extract_corpus(documents_dir)
chapter_num_dict = extracted_documents[1]
documents = extracted_documents[0]
chosen_document_num = chapter_num_dict[chosen_document_name]
chosen_document = documents[chosen_document_num]
# print(chosen_document)

# please run python -m spacy download en_core_web_trf and en_core_web_lg and python -m coreferee download en before running this script
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("coreferee")
doc = nlp(chosen_document)

resolved_text = ""

for token in doc:
    repres = doc._.coref_chains.resolve(token)
    if repres:
        print("Original Text", token.text, "coreferenced" , repres)
        resolved_text += " " + " and ".join([t.text for t in repres])
    else:
        if "—" in token.text:
            print("Detected", token.text)
            new_text = token.text.replace("—", "-")
            resolved_text += " " + new_text
        else:
            resolved_text += " " + token.text

resolved_text_path = Path(corpus_dir)/ "resolved_chapters" / f"{chosen_doc_name_wo_ext}_resolved.txt"


resolved_text_file = open(resolved_text_path, "w")
resolved_text_file.write(resolved_text)
