import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import json

from dotenv import load_dotenv
load_dotenv()  ##Load all the environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def handle_malformed_json(response_text):
  """Handles malformed JSON by adding double quotes around property names."""
  try:
    return json.loads(response_text)
  except json.JSONDecodeError:
    # Assuming the format is consistent, add double quotes around keys
    fixed_response = response_text.replace(":", '":')
    fixed_response = '{' + fixed_response + '}'
    return json.loads(fixed_response)


## Gemini Pro Response
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    try:
        response = model.generate_content(input)
        return handle_malformed_json(response.text)
    except Exception as e:
        st.error(f"Error getting Gemini response: {e}")
        return None



def input_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:  # Using a simple for loop
            text += str(page.extract_text())
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None


##Prompt Template
input_prompt = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide
best assistant for improving the resumes. Assign the percentage Matching based on JD and the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match:"%","MissingKeywords:[]","Profile Summary":""}}
"""

##streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        if text:
            response = get_gemini_response(input_prompt.format(text=text, jd=jd))
            if response:
                # Handle potential missing keys gracefully
                jd_match = response.get("JD Match", "Not available")  # Use get() with default value
                missing_keywords = response.get("MissingKeywords", [])  # Use get() with empty list default
                profile_summary = response.get("Profile Summary", "")  # Use get() with empty string default
                st.subheader("JD Match: {}".format(jd_match))
                st.subheader("Missing Keywords: {}".format(", ".join(missing_keywords)))
                st.subheader("Profile Summary: {}".format(profile_summary))
            else:
                st.error("No response from Gemini")
        else:
            st.error("Error extracting text from PDF")