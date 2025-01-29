import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from dynamo.attributeExtractor.constants import prompt_template
import json

class AttributeExtractor:
    def __init__(self):
        self.model_name = "meta-llama/Llama-3.2-3B-Instruct"
        if torch.cuda.is_available():
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.pipe = pipeline("text-generation",
                model=model,
                device=device,
                tokenizer=tokenizer,
                temperature=0.2,    # Reduce creativity
                max_new_tokens=100,  # Limit response length
                # eos_token_id = tokenizer.convert_tokens_to_ids("")
                )

    def generate_prompt(self, input):
        input_prompt = {
        "role": "human",
        "content": f"""
        Input: {input}
        Output:"""
        }
        full_prompt = prompt_template + [input_prompt]
        return full_prompt
        
    def parse_output(self, output):
        generated_content = output[0]['generated_text'][-1]['content']
        if "Input:" in generated_content:
            generated_content = generated_content.split("Input:", 1)[0]
            generated_content = generated_content.strip()
        output = generated_content.replace("'", '"')
        try:
            parsed_output = json.loads(output)
            return parsed_output
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {}

    def extract_attributes(self, input):
        prompt = self.generate_prompt(input)
        output = self.pipe(prompt)
        parsed_output = self.parse_output(output)
        return parsed_output

if __name__ == "__main__":
    ae = AttributeExtractor()
    input = "Take for example an 8-foot screw propeller having an 8-foot pitch at its largest diameter."
    new_attribute = ae.extract_attributes(input)
    print(new_attribute)