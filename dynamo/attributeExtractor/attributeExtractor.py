import os
from transformers import pipeline, StoppingCriteria, StoppingCriteriaList, AutoTokenizer
from langchain_huggingface import HuggingFacePipeline
from langchain.schema.runnable import RunnableSequence
from langchain_core.output_parsers.json import SimpleJsonOutputParser
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

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
model_name = "meta-llama/Llama-2-7b-chat-hf"
model_name = "meta-llama/Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)

pipe = pipeline("text-generation",
                model=model_name,
                tokenizer=tokenizer,
                temperature=0.2,    # Reduce creativity
                max_new_tokens=100,  # Limit response length
                eos_token_id = tokenizer.convert_tokens_to_ids("#")
                )

llm = HuggingFacePipeline(pipeline=pipe)
system_setting = SystemMessage(
    content =  "You are a world class algorithm for value attribute extraction for engineering documents in structured formats."
)
human_task_prompt = HumanMessage(
    f"""
    Extract the value attribute pairs for each entity in the given sentences, and respond with a JSON object. If an attribute is not present in the input sentence, return an empty JSON.  Do not generate additional questions or text. An example is as follows:
    Input: The engine is a Bleriot, with 5 hp and weighs 5.5kg.
    Output: {schema}
    """
)
human_message_prompt = HumanMessagePromptTemplate.from_template(
    """
    Input: {input}
    """)
prompt = ChatPromptTemplate(messages = [system_setting, human_task_prompt, human_message_prompt])

chain = prompt | llm

input = "A chair has 5 wheels."

print(chain.invoke({'input': input}))


# "jinja2.exceptions.TemplateError: Conversation roles must alternate user/assistant/user/assistant/..."