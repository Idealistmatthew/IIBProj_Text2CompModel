import os
from transformers import pipeline

schema = {
    "name": "engine",
    "attributes": [
        {
            "name": "power",
            "type": "int",
            "unit": "hp",
            "value": 5
        },
        {
            "name": "weight",
            "type": "float",
            "unit": "kg",
            "value": 5.5
        },
        {
            "name": "model",
            "type": "str",
            "value": "Bleriot"
        }
    ]
}

messages = [{
        "role": "system",
        "content": "You are an value attribute extractor for engineering documents. You return value attribute pairs using the following schema: {schema}"
    },
    {
        "role": "user",
        "content": "Extract the value attribute pairs for each entity in the following text, and respond with a JSON object."
    },
    {
        "role": "user",
        "content": "Gliders as a rule have only one rudder, and this is in the rear."
    }]


pipe = pipeline("text-generation", model="meta-llama/Llama-2-7b-chat-hf")
pipe(messages)



