from transformers import AutoTokenizer, AutoModel
from peft import PeftModel
tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b/", trust_remote_code=True)

schema1=""
schema2=""
schema_tag_edge=""


with open('schema/schema1') as f:
    schema1=f.read()

with open('schema/schema2') as f:
    schema2=f.read()

prompt = "<instruction>:根据输入提问生成对应的nGQL语句\n"
schema_new = schema1 + schema2
prompt += '<schema>:' + schema_new + "\n"
prompt += '<input>:' + "找出所有与球员'Messi'服务于同一个球队的球员，并返回这些球员的信息"+"\n<output>:"


model = AutoModel.from_pretrained("THUDM/chatglm2-6b/", trust_remote_code=True).half().cuda()
model = model.eval()


model_8 = PeftModel.from_pretrained(model, "weight/NL2GQL_ChatGLM2_v1.0/lora_8")
model_8=model_8.eval()
response, history = model_8.chat(tokenizer, prompt, history=[])
print("lora_8:\n"+response)
print()


model_16 = PeftModel.from_pretrained(model, "weight/NL2GQL_ChatGLM2_v1.0/lora_16")
model_16=model_16.eval()
response, history = model_16.chat(tokenizer, prompt, history=[])
print("lora_16\n:"+response)
print()


