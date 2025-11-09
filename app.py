import os
import streamlit as st
import PyPDF2
import google.generativeai as genai

# Set up Google Gemini API Key
GEMINI_API_KEY = "AIzaSyAQlEKIu-QbsZnOIxK1Yaw1JICgWSN9G7o"
genai.configure(api_key=GEMINI_API_KEY)

# Streamlit UI
st.set_page_config(page_title="Personal Finance Assistant", page_icon="💰", layout="wide")

# Custom CSS for Styling
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 34px;
        font-weight: bold;
        color: #4CAF50;
        text-shadow: 2px 2px 5px rgba(76, 175, 80, 0.4);
    }
    .sub-title {
        text-align: center;
        font-size: 18px;
        color: #ddd;
        margin-bottom: 20px;
    }
    .stButton button {
        background: linear-gradient(to right, #4CAF50, #388E3C);
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton button:hover {
        background: linear-gradient(to right, #388E3C, #2E7D32);
    }
    .result-card {
        background: rgba(0, 150, 136, 0.1);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0px 2px 8px rgba(0, 150, 136, 0.2);
    }
    .success-banner {
        background: linear-gradient(to right, #2E7D32, #1B5E20);
        color: white;
        padding: 15px;
        font-size: 18px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-top: 15px;
        box-shadow: 0px 2px 8px rgba(0, 150, 136, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<h1 class="main-title">💰 Personal Finance Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload your Transaction History PDF for Financial Insights eg:-Paytm </p>', unsafe_allow_html=True)

# Upload PDF File
uploaded_file = st.file_uploader("📂 Upload PDF File", type=["pdf"], help="Only PDF files are supported")

def extract_text_from_pdf(file_path):
    """Extracts text from the uploaded PDF file."""
    text = ""
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def analyze_financial_data(text):
    """Sends extracted text to Google Gemini AI for financial insights."""
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""
    Analyze the following Paytm transaction history and generate financial insights:
    {text}
    Provide a detailed breakdown in the following format:
    *Financial Insights for [User Name]*
    *Key Details:*
    - *Overall Monthly Income & Expenses:*
      - Month: [Month]
      - Income: ₹[Amount]
      - Expenses: ₹[Amount]
    - *Unnecessary Expenses Analysis:*
      - Expense Category: [Category Name]
      - Amount: ₹[Amount]
      - Recommendation: [Suggestion]
    - *Savings Percentage Calculation:*
      - Savings Percentage: [Percentage] %
    - *Expense Trend Analysis:*
      - Notable Trends: [Trend Details]
    - *Cost Control Recommendations:*
      - Suggestion: [Detailed Suggestion]
    - *Category-Wise Spending Breakdown:*
      - Category: [Category Name] - ₹[Amount]
    """
    response = model.generate_content(prompt)
    return response.text.strip() if response else "⚠ Error processing financial data."

# Processing Section
if uploaded_file is not None:
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ File uploaded successfully!")

    with st.spinner("📄 Extracting text from document..."):
        extracted_text = extract_text_from_pdf(file_path)

    if not extracted_text:
        st.error("⚠ Failed to extract text. Ensure the document is not a scanned image PDF.")
    else:
        progress_bar = st.progress(0)
        with st.spinner("🧠 AI is analyzing your financial data..."):
            insights = analyze_financial_data(extracted_text)

        progress_bar.progress(100)

        st.subheader("📊 Financial Insights Report")
        st.markdown(f'<div class="result-card"><b>📄 Financial Report for {uploaded_file.name}</b></div>', unsafe_allow_html=True)

        st.write(insights)

        st.markdown('<div class="success-banner">🎉 Analysis Completed! Plan your finances wisely. 🚀</div>', unsafe_allow_html=True)
        st.balloons()

    os.remove(file_path)  # Cleanup

