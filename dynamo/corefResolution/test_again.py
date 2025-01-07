
import spacy

nlp = spacy.load("en_core_web_trf")
nlp.add_pipe("coreferee")
doc = nlp("—")

resolved_text = ""

for token in doc:
    repres = doc._.coref_chains.resolve(token)
    if repres:
        print("Original Text", token.text, "coreferenced" , repres)
        resolved_text += " " + " and ".join([t.text for t in repres])
    else:
        if token.pos_ == "PUNCT":
            print("Punctuation", token.text)
        resolved_text += " " + token.text

resolved_text_file = open("test.txt", "w")
resolved_text_file.write(resolved_text)
