import os
from dynamo.secret_constants.api_keys import OPEN_AI_KEY
from openai import OpenAI

client = OpenAI(
    api_key=OPEN_AI_KEY
)

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

print(schema)

completion = client.chat.completions.create(
    model = "gpt-3.5-turbo",
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
    }],
)

print(completion.choices[0].message)


