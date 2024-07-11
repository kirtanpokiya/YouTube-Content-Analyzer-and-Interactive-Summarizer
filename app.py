import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Configure the API key for the generative AI model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to fetch and combine the YouTube transcript data
def fetch_youtube_transcript(video_url):
    try:
        video_id = video_url.split("=")[1]
        transcript_segments = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ""
        for segment in transcript_segments:
            transcript_text += " " + segment["text"]
        return transcript_text
    except Exception as e:
        return str(e)

# Define the prompt for summarizing the transcript
summary_prompt = "You are a YouTube video summarizer. Summarize the provided YouTube transcript text in bullet points."

# Define the prompt for asking questions about the transcript
question_prompt = "You are an assistant that answers questions based on YouTube transcript text. Given the transcript text and a question, provide a detailed answer."

# Function to generate summary using the generative AI model
def generate_summary_from_transcript(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    result = model.generate_content(prompt + transcript_text)
    return result.text

# Function to generate answers to questions using the generative AI model
def generate_answer_from_transcript(transcript_text, question, prompt):
    model = genai.GenerativeModel("gemini-pro")
    result = model.generate_content(prompt + transcript_text + " Question: " + question)
    return result.text

# Streamlit app title
st.title("YouTube Content Analyzer and Query System")

# Input field for YouTube video URL
st.write("## Step 1: Enter the YouTube Video URL")
video_url_input = st.text_input("Enter the URL of the YouTube video")

# Display video thumbnail if URL is provided
if video_url_input:
    try:
        video_id = video_url_input.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except IndexError:
        st.error("Invalid URL. Please enter a valid YouTube video URL.")

# Fetch transcript
transcript_text = ""
if video_url_input:
    with st.spinner("Fetching video transcript..."):
        transcript_text = fetch_youtube_transcript(video_url_input)
        if "Could not retrieve" in transcript_text:
            st.error("Could not retrieve transcript. Please check the URL or try again later.")

# Button to fetch summary
if transcript_text and st.button("Generate Summary"):
    with st.spinner("Generating summary..."):
        video_summary = generate_summary_from_transcript(transcript_text, summary_prompt)
        st.write("### Summary")
        st.write(video_summary)

# Section for asking questions
st.write("## Step 2: Ask Questions About the Video")
question_input = st.text_input("Enter your question here")

# Button to get answer to the question
if transcript_text and question_input and st.button("Get Answer"):
    with st.spinner("Generating answer..."):
        answer = generate_answer_from_transcript(transcript_text, question_input, question_prompt)
        st.write("### Answer")
        st.write(answer)