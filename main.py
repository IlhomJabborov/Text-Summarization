from fastapi import FastAPI
from transformers import pipeline
from bs4 import BeautifulSoup
import requests
from fastapi.responses import JSONResponse

app = FastAPI()
summarizer = pipeline("summarization")

@app.get("/")
async def root():
    return {"message": "route /summarize?url={URL} to summarize the article at the given URL.Documentation at /docs route"}

@app.get("/summarize")
async def get_summary(url: str):
    try :
        r = requests.get(url)
        soup = BeautifulSoup(r.text,'html.parser')
        results = soup.find_all(['h1','p'])

        soup = BeautifulSoup(r.text,'html.parser')
        results = soup.find_all(['h1','p'])

        text = [result.text for result in results]
        ARTICLE = ' '.join(text)

        ARTICLE = ARTICLE.replace('.','<eos>')
        ARTICLE = ARTICLE.replace('!','<eos>')
        ARTICLE = ARTICLE.replace('?','<eos>')
        sentences = ARTICLE.split('<eos>')


        max_chunk = 500
        current_chunk = 0
        chunks = []

        for sentence in sentences:
            if len(chunks) == current_chunk + 1:
                if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                    chunks[current_chunk].extend(sentence.split(' '))
                else:
                    current_chunk += 1
                    chunks.append(sentence.split(' '))
            else:
                chunks.append(sentence.split(' '))

        for chunk_id in range(len(chunks)) :
            chunks[chunk_id] = ' '.join(chunks[chunk_id])

        res = summarizer(chunks, max_length=80, min_length=30, do_sample=False)


        summary = ' '.join([summ['summary_text'] for summ in res])

        return {"summary": summary}
    
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": "Invalid URL"})