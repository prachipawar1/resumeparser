

import streamlit as st
import spacy
from pdfminer.high_level import extract_text
import re
import fitz  # PyMuPDF
from spacy.matcher import Matcher

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        text = extract_text(pdf_path)
        if text:
            return text
        else:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

# Function to extract information
def extract_info(text):
    doc = nlp(text)
    info = {}

    # Extract name using the Matcher
    matcher = Matcher(nlp.vocab)
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    matcher.add("NAME", [pattern])
    matches = matcher(doc)
    name = None
    for match_id, start, end in matches:
        name = doc[start:end].text
        break
    info["Name"] = name if name else "N/A"

    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    info["Email"] = email_matches[0] if email_matches else "N/A"

    # Extract phone numbers
    phone_pattern = r'\b\d{10}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b'
    phone_matches = re.findall(phone_pattern, text)
    info["Phone"] = phone_matches[0] if phone_matches else "N/A"

    # Extract skills (simplified)
    skills = [token.text for token in doc if token.pos_ == "NOUN" and token.ent_type_ == ""]
    info["Skills"] = ', '.join(skills) if skills else "N/A"

    # Extract experience (simplified, looks for patterns like "X years of experience")
    experience_pattern = r'\b\d+\s+years?\s+of\s+experience\b'
    experience_matches = re.findall(experience_pattern, text.lower())
    info["Experience"] = experience_matches[0] if experience_matches else "N/A"

    # Extract college, degree, designation, and company names
    info["College"] = extract_college(text)
    info["Degree"] = extract_degree(text)
    info["Designation"] = extract_designation(text)
    info["Company"] = extract_company(text)

    return info

# Helper functions for specific extractions
def extract_college(text):
    # Add logic to extract college names
    college_pattern = r'\b(?:University|College|Institute|School)\b.*'
    college_matches = re.findall(college_pattern, text, re.IGNORECASE)
    return college_matches[0] if college_matches else "N/A"

def extract_degree(text):
    # Add logic to extract degrees
    degree_pattern = r'\b(?:B\.?Sc|M\.?Sc|B\.?Tech|M\.?Tech|Ph\.?D|Bachelor|Master|Doctor)\b.*'
    degree_matches = re.findall(degree_pattern, text, re.IGNORECASE)
    return degree_matches[0] if degree_matches else "N/A"

def extract_designation(text):
    # Add logic to extract designations
    designation_pattern = r'\b(?:Manager|Engineer|Developer|Consultant|Analyst|Intern)\b.*'
    designation_matches = re.findall(designation_pattern, text, re.IGNORECASE)
    return designation_matches[0] if designation_matches else "N/A"

def extract_company(text):
    # Add logic to extract company names
    company_pattern = r'\b(?:Inc|Corp|LLC|Ltd|Technologies|Systems|Enterprises|Group|Solutions|Services)\b.*'
    company_matches = re.findall(company_pattern, text, re.IGNORECASE)
    return company_matches[0] if company_matches else "N/A"

# Streamlit app
def main():
    st.title("Resume Parser")

    uploaded_file = st.file_uploader("Upload a resume (PDF)", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner("Extracting text from PDF..."):
            text = extract_text_from_pdf(uploaded_file)
        
        if text:
            with st.spinner("Extracting information from resume..."):
                info = extract_info(text)

            st.subheader("Extracted Information")
            for key, value in info.items():
                st.write(f"**{key}:** {value}")
        else:
            st.error("Could not extract text from the uploaded PDF.")

if __name__ == "__main__":
    main()
