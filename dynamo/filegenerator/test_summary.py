# import spacy
# import pytextrank

# nlp = spacy.load("en_core_web_sm")
# nlp.add_pipe("textrank")

# text = (
#     "Unlike the rudder on a boat it is fixed and immovable. The real motor-propelled flying machine, "
#     "generally has both front and rear rudders manipulated by wire cables at "
#     "the will of the operator. Allowing that the amateur has become reasonably expert in the manipulation "
#     "of the glider he should, before constructing an actual flying machine, "
#     "equip his glider with a rudder."
# )
# print(text)

# doc = nlp(text)

# for sentence in doc._.textrank.summary():
#     print(sentence)

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

text = (
    "Unlike the rudder on a boat it is fixed and immovable. The real motor-propelled flying machine, "
    "generally has both front and rear rudders manipulated by wire cables at "
    "the will of the operator. Allowing that the amateur has become reasonably expert in the manipulation "
    "of the glider he should, before constructing an actual flying machine, "
    "equip his glider with a rudder."
)

text = """The rudder beams form the top and bottom frames of the vertical rudder.This rudder beam is 8 feet 11 inches long.Now , from the outer ends of the rudder frame run four similar diagonal wires to the end of the rudder beam where beam rests on the cross piece ."""

parser = PlaintextParser.from_string(text, Tokenizer("english"))
summarizer = LsaSummarizer()
summary = summarizer(parser.document, 2)
sentence_str = ""
for sentence in summary:
    sentence_str += str(sentence)

print(sentence_str)

# print(text_summary)
# print(summarizer(parser.document, 2))