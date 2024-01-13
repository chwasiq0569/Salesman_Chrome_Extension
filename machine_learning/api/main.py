from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request
import utils
import models
import numpy as np
from scraper.scrape import scrape

app = FastAPI()
# st.set_page_config(page_title='Multilanguage Text Analyzer')
# st.header('Multilanguage Text Analyzer')

# if 'conversation_history' not in st.session_state:
#  st.session_state['conversation_history'] = []


# input = st.text_input("Question: ", key="question")
# text = st.text_area("Text: ", key="text")
# submit = st.button("Analyze Text")

input_prompts = """You will act as a Salesperson. The Product Details and question will be provided to you. You have to answer the questions according to the provided product details briefly but correct like a Salesman. Dont return markdown just return a paragraph
"""

# if submit and input and text:
#   response = get_gemini_response(input_prompts, text, input)
#   st.session_state['conversation_history'].append(("User", f"Question: {input}\n\nText: {text}"))
#   st.subheader("The Response is ")
#   st.write(response)
#   st.session_state['conversation_history'].append(("Bot", response))

# st.subheader("The Conversation History is")
# for role, text in st.session_state['conversation_history']:
#  st.write(f"{role}: {text}")

# origins = ["http://localhost:3000"]  # Allow requests from this origin

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scrape_site")
async def process_data(request: Request):
    data = await request.json()
    context = scrape(data['link'])
    return { "context": context }  


@app.post("/process_data")
async def process_data(request: Request):
    # scrape(weblink)
    data = await request.json()
        # Perform some operations with the parameters
        # result = data['param1'] + data['param2']
        # Return the result
        # return {"result": result}
    # context = scrape(data['link'])
    # return { "result": context }
    reviews = utils.extract_text_after_word("CUSTOMER_REVIEWS=> ", data['context'])

    new_list = reviews.split("Read more")

    new_list = [i for i in new_list if i]
    
    if data['context']:
        response = models.get_gemini_response(input_prompts, data['question'], data['context'])
        return { 
            "result": response
            }

    return { 
            "result": "Something went wrong while fetching the product"
             }
    

@app.post("/sentiment-analysis")
async def sentimentsAnalysis(request: Request):
    data = await request.json()
    # context = scrape(data['link'])
    reviews = utils.extract_text_after_word("CUSTOMER_REVIEWS=> ", data['context'])
    new_list = reviews.split("Read more")
    new_list = [i for i in new_list if i]
    
    review_sentiments = []

    for review in new_list:
        review_sentiments.append(models.sentiment_model(review))

    return {"reviews": utils.max_values(review_sentiments), "reviews_length": len(new_list) }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)