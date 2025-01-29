import os
# from guidance import models, gen
from transformers import pipeline, StoppingCriteria, StoppingCriteriaList, AutoTokenizer, AutoModelForCausalLM
from langchain_huggingface import HuggingFacePipeline
from langchain.schema.runnable import RunnableSequence
from langchain_core.output_parsers.json import SimpleJsonOutputParser
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
import torch
import json

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

# messages = [{
#         "role": "system",
#         "content": "You are an value attribute extractor for engineering documents. You return value attribute pairs using the following schema: {schema}"
#     },
#     {
#         "role": "human",
#         "content": "Extract the value attribute pairs for each entity in the following text, and respond with a JSON object." 
#     },
#     {
#         "role": "human",
#         "content": "Gliders as a rule have only one rudder, and this is in the rear."
#     }]
if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

model_name = "meta-llama/Llama-2-7b-chat-hf"
model_name = "meta-llama/Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# # Define a custom stopping criterion for a period
# class StopOnMessage(StoppingCriteria):
#     def __init__(self, tokenizer):
#         self.stop_token_id = tokenizer.convert_tokens_to_ids("<|start_header_id|>")
#         print(self.stop_token_id)

#     def __call__(self, input_ids, scores, **kwargs):
#         # Stop when a period is generated
#         print(input_ids[0][-1])
#         return input_ids[0][-1] == self.stop_token_id

pipe = pipeline("text-generation",
                model=model,
                device=device,
                tokenizer=tokenizer,
                temperature=0.2,    # Reduce creativity
                max_new_tokens=100,  # Limit response length
                # eos_token_id = tokenizer.convert_tokens_to_ids("")
                )

# llm = HuggingFacePipeline(pipeline=pipe)
# system_setting = SystemMessage(
#     content =  "You are a world class algorithm for value attribute extraction for engineering documents in structured formats."
# )
# human_task_prompt = HumanMessage(
#     f"""
#     Extract the value attribute pairs for each entity in the given sentences, and respond with a JSON object. If an attribute is not present in the input sentence, return an empty JSON.  Do not generate additional questions or text. An example is as follows:
#     Input: The engine is a Bleriot, with 5 hp and weighs 5.5kg.
#     Output: {schema}
#     """
# )
# human_message_prompt = HumanMessagePromptTemplate.from_template(
#     """
#     This is the only prompt
#     Input: {input}
#     Output:
#     """)
# prompt = ChatPromptTemplate(messages = [system_setting, human_task_prompt, human_message_prompt])

messages = [{
        "role": "system",
        "content": "You are a world class algorithm for value attribute extraction for engineering documents in structured formats."
    },
    {
        "role": "human",
        "content": f"""
    Extract the value attribute pairs for each entity in the given sentences, and respond with a JSON object. If an attribute is not present in the input sentence, return an empty JSON and nothing else.  Do not generate additional inputs, questions or text. The following is an example:
    Input: The engine is a Bleriot, with 5 hp and weighs 5.5kg.
    Output: {schema}
    """
    },
    {
        "role": "human",
        "content": """
        Input: A chair has 5 wheels.
        Output:"""
    }]


generation = pipe(messages)
output_json = generation[0]['generated_text'][-1]['content']
print(output_json)
try:
    output_json = output_json.replace("'", '"')
    parsed_output = json.loads(output_json)
    print(parsed_output)
except json.JSONDecodeError as e:
    print(f"Failed to parse JSON: {e}")

new_messages = [{
        "role": "system",
        "content": "You are a world class algorithm for value attribute extraction for engineering documents in structured formats."
    },
    {
        "role": "human",
        "content": f"""
    Extract the value attribute pairs for each entity in the given sentences, and respond with a JSON object. If an attribute is not present in the input sentence, return an empty JSON.  Do not generate additional questions or text. An example is as follows:
    Input: The engine is a Bleriot, with 5 hp and weighs 5.5kg.
    Output: {schema}
    """
    },
    {
        "role": "human",
        "content": """
        Input: This is just a random sentence.
        Output:"""
    }]

generation = pipe(new_messages)
output_json = generation[0]['generated_text'][-1]['content']
if "Input:" in output_json:
    output_json = output_json.split("Input:", 1)[0]
    output_json = output_json.strip()
print(output_json)
try:
    parsed_output = json.loads(output_json)
    print(parsed_output)
except json.JSONDecodeError as e:
    print(f"Failed to parse JSON: {e}")


# chain = prompt | llm

# input = "A chair has 5 wheels."

# print(chain.invoke({'input': input}))


# "jinja2.exceptions.TemplateError: Conversation roles must alternate user/assistant/user/assistant/..."