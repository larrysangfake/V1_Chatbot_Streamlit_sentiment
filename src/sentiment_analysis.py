import streamlit as st
from transformers import pipeline

# Initialize sentiment analysis pipeline
@st.cache_resource
def load_pipeline():
    return pipeline("sentiment-analysis")

sentiment_analyzer = load_pipeline()

st.title("Sentiment Analysis App")
st.write("Enter text below to analyze its sentiment.")

# Text input
text = st.text_area("Enter your text here:")

if st.button("Analyze"):
    if text:
        results = sentiment_analyzer(text)
        for result in results:
            st.write(f"Label: {result['label']}, Score: {result['score']:.4f}")
    else:
        st.write("Please enter some text for analysis.")
