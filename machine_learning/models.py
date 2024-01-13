from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax
import numpy as np
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

def sentiment_model(review):
    MODEL = os.environ['SENTIMENT_ANALYSIS_MODEL']
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    encoded_text = tokenizer(review, return_tensors='pt', truncation=True, max_length=512)
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    probabilities = {'roberta_neg': np.float32(0.0033037418), 'roberta_neu': np.float32(0.022949861), 'roberta_pos': np.float32(0.9737464)}
    print(review[:10])
    # print({key: float(val) for key, val in probabilities.items()})
    print({key: float(score) for key, score in zip(['roberta_neg', 'roberta_neu', 'roberta_pos'], scores)})
    return {key: float(score) for key, score in zip(['roberta_neg', 'roberta_neu', 'roberta_pos'], scores)}
    # return {  seperate_reviews({key: float(score) for key, score in zip(['roberta_neg', 'roberta_neu', 'roberta_pos'], scores)}) }
    # return {key: float(val) for key, val in probabilities.items()}

def get_gemini_response(input, text, prompt):
  genai.configure(api_key=os.environ['GEMINI_API_KEY'])
  model = genai.GenerativeModel('gemini-pro')
  response = model.generate_content([input, text, prompt])
  return response.text