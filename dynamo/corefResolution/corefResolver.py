from dynamo.util.chapter_split import extract_document
import spacy

def resolve_coref(document_path, resolved_path):
    document = extract_document(document_path)
    
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("coreferee")
    doc = nlp(document)

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
    
    resolved_text_file = open(resolved_path, "w")
    resolved_text_file.write(resolved_text)

