from transformers import pipeline
import re

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def retelling(description):
    article_text = re.sub(r'<img.*?>', '', description)
    print(article_text)
    summary = summarizer(article_text, max_length=250, min_length=30, do_sample=False)
    return summary
