
import openai
from Config import *
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.utils import GenerationConfig
import requests
# from peft import PeftModel, PeftConfig
'''
Deployment Plan for 7B-Scale Models - Further optimization for vllm deployment can be considered.
chat: Local deployment of the original model.
chat_with_api: Remote deployment with API connectivity.
'''

class SMALLER_LLM:
    def __init__(self):
        print('Initializing...')
        self.model_path = SLLM_MODEL_PATH
        self.api_url = API_URL

        # Check if API usage is disabled
        if not USE_API:
            # Initialize tokenizer and model from the local path
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, use_fast=False, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path, device_map=DEVICE_MAP, torch_dtype=torch.bfloat16, trust_remote_code=True)
            self.model.generation_config = GenerationConfig.from_pretrained(self.model_path)

        # Check if LORA model is to be used and LORA_PATH is provided
        if USE_LORA and LORA_PATH != "":
            # Load the model from LORA_PATH
            self.model = PeftModel.from_pretrained(self.model, LORA_PATH)

    def chat(self, text):
        messages = []
        messages.append({"role": "user", "content": text})
        response = self.model.chat(self.tokenizer, messages)
        return response[0]

    def chat_with_api(self, text):
        # Set the OpenAI API base and key for remote deployment
        openai.api_base = "http://xxxx:8000/v1"  # Replace with your service's IP
        openai.api_key = "xxxx"  # Fill in your API key here

        # Create a ChatCompletion request with the user's text
        completion = openai.ChatCompletion.create(
            model=SLLM_MODEL_NAME,
            messages=[
                {"role": "user", "content": text},
            ],
            stream=False,
        )

        # Retrieve and return the generated content
        return completion.choices[0].message.content