import os
import tempfile
import streamlit as st
import PyPDF2
import google.generativeai as genai

# =========================
# 🚀 Streamlit Page Setup
# =========================
st.set_page_config(page_title="💸 Personal Financial Analyzer", layout="wide")

# --- Lazy Background Load ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f9f9f9;
    background-image: url("https://images.unsplash.com/photo-1508385082359-f38ae991e8f5?auto=format&fit=crop&w=1350&q=80");
    background-size: cover;
    background-position: center;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.main-title { text-align:center; font-size:50px; font-weight:bold; color:#000; }
.sub-title { text-align:center; font-size:18px; color:#000; margin-bottom:20px; }
.success-banner {
    background: rgba(0,150,136,0.1);
    padding: 15px; border-radius: 8px;
    text-align:center; font-weight:bold; margin-top:15px;
    box-shadow: 0 2px 8px rgba(0,150,136,0.2);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Personal Financial Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">📊 Powered by Google Gemini AI</p>', unsafe_allow_html=True)


# =========================
# 🔑 Gemini API Configuration
# =========================
if "gemini_configured" not in st.session_state:
    gemini_api_key = st.text_input("🔑 Enter your Gemini API Key:", type="password")
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        st.session_state.gemini_configured = True
        st.success("✅ Gemini API Key configured successfully!")
    else:
        st.warning("Enter your Gemini API key to continue.")
        st.stop()
else:
    gemini_api_key = None  # already configured


# =========================
# 📄 PDF Text Extraction
# =========================
def extract_text_from_pdf(file_path):
    """Extract text quickly from a text-based PDF."""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        st.error(f"❌ PDF extraction failed: {e}")
        return ""


# =========================
# 🧠 Gemini Analysis
# =========================
@st.cache_resource(show_spinner=False)
def get_gemini_model():
    """Cache the Gemini model for speed."""
    return genai.GenerativeModel("gemini-1.5-flash")

@st.cache_data(show_spinner=False)
def analyze_financial_data(text):
    """Analyze extracted financial data using Gemini."""
    try:
        model = get_gemini_model()
        prompt = f"""
You are a financial data analyst AI.
Analyze this UPI or bank statement and summarize it clearly.

### Input:
{text[:8000]}

### Output (in markdown format):

# Financial Insights
## Monthly Overview
| Month | Income (₹) | Expenses (₹) | Savings (%) |

## Key Trends
- ...

## Recommendations
- ...

## Category Breakdown
| Category | Amount (₹) |
|-----------|------------|
"""
        response = model.generate_content(prompt)
        return response.text.strip() if response else "⚠️ No response from AI."
    except Exception as e:
        return f"⚠️ Gemini Analysis Error: {e}"


# =========================
# 📂 File Upload & Analysis
# =========================
uploaded_file = st.file_uploader("📁 Upload your UPI or Bank Statement (PDF)", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    with st.spinner("🔍 Extracting text from your PDF..."):
        extracted_text = extract_text_from_pdf(tmp_path)

    if not extracted_text.strip():
        st.error("⚠️ Could not extract text. Try a text-based PDF (not scanned).")
        os.remove(tmp_path)
        st.stop()

    st.success("✅ PDF text extracted successfully!")
    st.markdown('<div class="success-banner">File Uploaded and Processed Successfully</div>', unsafe_allow_html=True)

    with st.expander("📜 View Extracted Text (Preview)"):
        st.text_area("Extracted PDF Text", extracted_text[:3000], height=200)

    analyze_btn = st.button("🤖 Analyze Financial Insights")

    if analyze_btn:
        progress = st.progress(10)
        with st.spinner("🧠 AI is analyzing your data..."):
            insights = analyze_financial_data(extracted_text)
        progress.progress(100)

        st.subheader("📊 AI Financial Report")
        st.markdown(insights, unsafe_allow_html=True)

        st.download_button(
            "📥 Download Report",
            data=insights,
            file_name="financial_analysis_report.md",
            mime="text/markdown"
        )
        st.markdown('<div class="success-banner">✅ Report Generated! Ready for Download.</div>', unsafe_allow_html=True)
        st.balloons()

    os.remove(tmp_path)
