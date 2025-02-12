from dynamo.util.chapter_split import extract_document
from autocorrect import Speller

nlp_data = {
    "ornithopter": 1,
    "cold": 1,
    "sky": 1,
    "blue": 1
}

spell = Speller()
spell.nlp_data.update(nlp_data)

text = "Hte ornithoper was cold and the sky was blue"

print(spell(text))

