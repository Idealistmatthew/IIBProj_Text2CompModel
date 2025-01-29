example_schema = {
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

prompt_template = [{
        "role": "system",
        "content": "You are a world class algorithm for value attribute extraction for engineering documents in structured formats."
        },
        {
            "role": "human",
            "content": f"""
        Extract the value attribute pairs for each entity in the given sentences, and respond with a JSON object. If an attribute is not present in the input sentence, return an empty JSON and nothing else.  Do not generate additional inputs, questions or text. The following is an example:
        Input: The engine is a Bleriot, with 5 hp and weighs 5.5kg.
        Output: {example_schema}
        """
        },]