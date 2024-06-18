
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from transformers import T5Tokenizer ,T5ForConditionalGeneration,DataCollatorForSeq2Seq

MODEL_NAME = "scientisthere/sap_currency_conversion_usecase"
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
os.environ["HF_TOKEN"] = "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"

def response(input,length):
    my_question =input
    inputs = "Please answer to this question: " + my_question
    inputs = tokenizer(inputs, return_tensors="pt")
    outputs = model.generate(**inputs,max_new_tokens=length)
    answer = tokenizer.decode(outputs[0])
    return answer.replace('<pad>','').replace('</s>','')