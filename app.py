import os
import tempfile
import streamlit as st
import PyPDF2
import google.generativeai as genai

# ========================
#  1️⃣  Secure Gemini Setup
# ========================
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    st.error("⚠️ Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
    st.stop()

genai.configure(api_key=gemini_api_key)

# ========================
#  2️⃣  Streamlit UI Setup
# ========================
st.set_page_config(page_title="Personal Financial Analyzer", layout="wide")

# 🖼️ Background Styling
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://hougumlaw.com/wp-content/uploads/2016/05/light-website-backgrounds-light-color-background-images-light-color-background-images-for-website-1024x640.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.main-title { text-align:center; font-size:50px; font-weight:bold; color:#000; }
.sub-title { text-align:center; font-size:18px; color:#000; margin-bottom:20px; }
.result-card, .success-banner {
    background: rgba(0,150,136,0.1); padding: 15px; border-radius: 8px;
    margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,150,136,0.2);
}
.success-banner {
    font-size: 18px; text-align: center; font-weight: bold; margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Personal Financial Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Powered By AI</p>', unsafe_allow_html=True)

# ========================
#  3️⃣  Helper Functions
# ========================

def extract_text_from_pdf(file_path):
    """Extracts text from PDF using PyPDF2."""
    text = ""
    try:
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        st.error(f"❌ PDF extraction failed: {e}")
        return ""
    return text.strip()

@st.cache_data(show_spinner=False)
def analyze_financial_data(text):
    """Send extracted text to Gemini for analysis."""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
You are a financial data analyst AI.
Analyze this UPI/Bank transaction statement and provide structured markdown insights.

Data:
{text}

Please output in **structured markdown**:

# Financial Insights Summary

## Monthly Overview
| Month | Income (₹) | Expenses (₹) | Savings (%) |


## Trends
- [Trend observations]

## Recommendations
- [Cost control tips]

## Category Breakdown
| Category | Amount (₹) |
|-----------|------------|
        """

        response = model.generate_content(prompt)
        return response.text.strip() if response else "⚠️ AI did not return a response."

    except Exception as e:
        return f"⚠️ Error while analyzing data: {e}"

# ========================
#  4️⃣  File Upload + Processing
# ========================
uploaded_file = st.file_uploader(
    "Upload your UPI/Bank Statement PDF for Insights",
    type=["pdf"],
    help="Only text-based (non-scanned) PDFs are supported."
)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name



    with st.spinner("📄 Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf(temp_path)

    if not extracted_text:
        st.error("⚠️ Could not extract text. Try using an OCR tool on your statement first.")
    else:
        #st.info("")
        st.markdown("""
    <div style="background: rgba(0, 150, 136, 0.1); color:black; padding:12px; border-radius:8px;">
         File Uploaded And Text Extracted Successfully...
    </div>
    """, unsafe_allow_html=True)

        progress = st.progress(10)
        with st.spinner("AI is analyzing your financial data..."):
            insights = analyze_financial_data(extracted_text)
        progress.progress(100)

        #st.subheader("📄 Financial Analysis Report")
        st.markdown(insights, unsafe_allow_html=True)

        st.download_button(
            "📥 Download Report (Markdown)",
            data=insights,
            file_name="financial_report.txt",
            mime="text/markdown"
        )

        st.markdown('<div class="success-banner">Report Generated! Optimize Your Spendings and Savings...</div>', unsafe_allow_html=True)
        st.balloons()

    os.remove(temp_path)
