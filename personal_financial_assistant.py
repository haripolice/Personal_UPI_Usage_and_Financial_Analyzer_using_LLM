import streamlit as st
import fitz  # PyMuPDF (much faster)
import google.generativeai as genai
import os

# ========================
# 1️⃣ Gemini API Configuration
# ========================
GEMINI_API_KEY = os.getenv("AIzaSyAQlEKIu-QbsZnOIxK1Yaw1JICgWSN9G7o")

if not GEMINI_API_KEY:
    st.error("⚠️ Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# ========================
# 2️⃣ Streamlit Page Setup
# ========================
st.set_page_config(page_title="Personal Financial Analyzer", layout="wide")

st.markdown("""
<h1 style="text-align:center; font-size:48px; color:#004d40;">💰 Personal Financial Analyzer</h1>
<p style="text-align:center; color:#00695c;">AI-powered financial summary for your UPI/Bank statements</p>
""", unsafe_allow_html=True)

# ========================
# 3️⃣ PDF Extraction (FAST)
# ========================
@st.cache_data(show_spinner=False)
def extract_text_from_pdf(file_bytes):
    """Extracts text from PDF bytes using PyMuPDF (fast)."""
    text = ""
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text")
    except Exception as e:
        st.error(f"❌ PDF extraction failed: {e}")
    return text.strip()

# ========================
# 4️⃣ Gemini AI Analysis
# ========================
@st.cache_data(show_spinner=False)
def analyze_with_gemini(text):
    """Send summarized text to Gemini for quick insights."""
    try:
        if len(text) > 20000:
            text = text[:20000]  # limit tokens for speed

        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
You are an expert financial analyst.
Analyze the following transaction data and provide a short, structured report in markdown.

Data:
{text}

Output should include:
- Key monthly spending summary
- Expense categories (approximate)
- Notable patterns or trends
- 3 short financial recommendations
        """

        response = model.generate_content(prompt)
        return response.text.strip() if response else "⚠️ No response received from Gemini."
    except Exception as e:
        return f"⚠️ Error: {e}"

# ========================
# 5️⃣ File Upload + Analysis
# ========================
uploaded_file = st.file_uploader("📤 Upload your UPI/Bank Statement PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("📄 Extracting text from your statement..."):
        pdf_bytes = uploaded_file.read()
        text = extract_text_from_pdf(pdf_bytes)

    if not text:
        st.error("No readable text found in PDF. Try exporting a text-based statement.")
        st.stop()

    st.success("✅ Text extracted successfully!")

    with st.expander("📜 View Extracted Text (for reference)", expanded=False):
        st.text_area("Extracted Text", text[:2000] + "..." if len(text) > 2000 else text, height=200)

    with st.spinner("🤖 Analyzing your financial statement using Gemini..."):
        insights = analyze_with_gemini(text)

    st.markdown("## 🧠 AI Financial Report")
    st.markdown(insights, unsafe_allow_html=True)

    st.download_button(
        "📥 Download Financial Report",
        data=insights,
        file_name="financial_analysis.md",
        mime="text/markdown"
    )

    st.balloons()
