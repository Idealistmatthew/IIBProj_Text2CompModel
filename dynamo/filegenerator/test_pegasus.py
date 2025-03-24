
from transformers import pipeline
from transformers import PegasusForConditionalGeneration, PegasusTokenizer

# Pick model
model_name = "google/pegasus-xsum"
# Load pretrained tokenizer
pegasus_tokenizer = PegasusTokenizer.from_pretrained(model_name)

example_text = (
    "Unlike the rudder on a boat it is fixed and immovable. The real motor-propelled flying machine, "
    "generally has both front and rear rudders manipulated by wire cables at "
    "the will of the operator. Allowing that the amateur has become reasonably expert in the manipulation "
    "of the glider he should, before constructing an actual flying machine, "
    "equip his glider with a rudder."
)

print('Original Document Size:',len(example_text))
# Define PEGASUS model
pegasus_model = PegasusForConditionalGeneration.from_pretrained(model_name)
# Create tokens
tokens = pegasus_tokenizer(example_text, truncation=True, padding="longest", return_tensors="pt")

# Generate the summary
encoded_summary = pegasus_model.generate(**tokens)

# Decode the summarized text
decoded_summary = pegasus_tokenizer.decode(encoded_summary[0], skip_special_tokens=True)

# Print the summary
print('Decoded Summary :',decoded_summary)

summarizer = pipeline(
    "summarization", 
    model=model_name, 
    tokenizer=pegasus_tokenizer, 
    framework="pt"
)

summary = summarizer(example_text, min_length=60, max_length=70)
print(summary[0]["summary_text"])

