import streamlit as st
from PyPDF2 import PdfReader
import io
import os
import getpass
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
if not os.environ.get("GOOGLE_API_KEY"): 
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

st.set_page_config(
    page_title="AI Resume Critiquer", page_icon=":pencil:", layout="centered"
)

st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you're targetting (optional)")

analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdfreader = PdfReader(pdf_file)
    text=""
    for page in pdfreader.pages:
        text += page.extract_text() + '\n'
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
        return text
    return uploaded_file.read().decode("utf-8")


if analyze:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop()
        
        prompt = f"""Please analyze this resume and provide constructive feedback. 
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'}

        Resume content: {file_content}

        Please provide your analysis in a clear, structured format with specific recommendations.
        """

        config = types.GenerateContentConfig(
            temperature = 0.7, 
            max_output_tokens = 1000,
            system_instruction = ["You are an expert resume reviewer with years of experience in HR and recruitment."]
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=config,
            contents=prompt
        )
        st.markdown("### Analysis Results")
        st.markdown(response.text)
    except Exception as e:
        st.error(f"An error occured: {str(e)}")
