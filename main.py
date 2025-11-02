import streamlit as st
import PyPDF2
import google.generativeai as genai
import re
import pandas as pd
import plotly.express as px
from datetime import datetime

# ✅ Import category mapping
from Category import category_keywords  # Ensure Category.py is in the same directory

# ---------------- PDF Extraction ----------------
def extract_text_from_pdf(file):
    """Extract text from PDF using PyPDF2"""
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"❌ PDF Extraction Error: {e}")
        return ""

# ---------------- Gemini AI Analysis ----------------
def analyze_financial_data(text, api_key):
    """Use Gemini AI to generate a financial analysis"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")  # ✅ Updated model name

        prompt = f"""
You are a certified financial analyst.
Analyze the following UPI transaction data and create a detailed professional financial report.

### Structure the report as follows:
1. **Executive Summary**
   - Overview of financial activity
   - Key highlights

2. **Income vs. Expenses**
   - Total credits, debits, and net cash flow

3. **Spending Analysis**
   - Top categories and merchants
   - Recurring patterns (like OTT, food delivery)

4. **Expense Efficiency**
   - Identify possible overspending areas

5. **Recommendations**
   - 3–5 practical savings or budgeting suggestions

6. **Conclusion**
   - High-level summary

Transaction Data:
{text}
        """

        response = model.generate_content(prompt)
        return response.text.strip() if response else "⚠️ No AI response received."
    except Exception as e:
        st.error(f"❌ Gemini Error: {e}")
        return ""

# ---------------- Detect Statement Type ----------------
def detect_statement_source(text):
    if "UPI Ref No" in text and "Total Money Paid" in text:
        return "Paytm"
    elif "Transaction ID" in text and "UTR No" in text:
        return "PhonePe"
    return "Unknown"

# ---------------- Extract Paytm/PhonePe Data ----------------
def extract_statement_period(text):
    match = re.search(r"(\w{3} \d{2}, \d{4}) - (\w{3} \d{2}, \d{4})", text)
    if match:
        try:
            start_date = datetime.strptime(match.group(1), "%b %d, %Y")
            end_date = datetime.strptime(match.group(2), "%b %d, %Y")
            return start_date, end_date
        except:
            return None, None
    return None, None

# ---------------- Parse PhonePe Transactions ----------------
def parse_phonepe_data(text):
    transactions = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    date_pattern = re.compile(r"^[A-Za-z]{3} \d{1,2}, \d{4}$")
    amount_pattern = re.compile(r"(?:INR|Rs\.?)\s*([\d,]+\.\d{2})")

    i = 0
    while i < len(lines):
        if date_pattern.match(lines[i]):
            date_str = lines[i]
            block = []
            i += 1
            while i < len(lines) and not date_pattern.match(lines[i]):
                block.append(lines[i])
                i += 1

            desc = " ".join(block)
            amt_match = amount_pattern.search(desc)
            amount = float(amt_match.group(1).replace(",", "")) if amt_match else 0.0
            txn_type = "Credit" if "credited" in desc.lower() else "Debit"

            category = "Other"
            for keyword, mapped_cat in category_keywords.items():
                if keyword in desc.lower():
                    category = mapped_cat
                    break

            try:
                date_obj = datetime.strptime(date_str, "%b %d, %Y")
            except:
                date_obj = None

            transactions.append({
                "Date": date_obj,
                "Description": desc[:60],
                "Amount": amount if txn_type == "Credit" else -amount,
                "Category": category,
                "Type": txn_type
            })
        else:
            i += 1
    return transactions

# ---------------- Parse Paytm Transactions ----------------
def parse_paytm_data(text):
    pattern = r"(\d{1,2} [A-Za-z]{3})\n(\d{1,2}:\d{2} [AP]M)(.*?)(?=\d{1,2} [A-Za-z]{3}\n\d{1,2}:\d{2} [AP]M|\Z)"
    matches = re.finditer(pattern, text, re.DOTALL)
    transactions = []

    for m in matches:
        date_str, time_str, details = m.groups()
        amount_match = re.search(r"([+-])\s?Rs\.?\s?(\d+(?:,\d{3})*(?:\.\d{2})?)", details)
        if amount_match:
            sign, amt = amount_match.groups()
            amount = float(amt.replace(",", ""))
            amount = -amount if sign == "-" else amount
        else:
            amount = 0.0

        desc = details.split("\n")[0].strip()
        category = next((v for k, v in category_keywords.items() if k in desc.lower()), "Other")
        transactions.append({
            "Date": date_str,
            "Description": desc,
            "Amount": amount,
            "Category": category,
            "Type": "Credit" if amount > 0 else "Debit"
        })
    return transactions

# ---------------- Visualization ----------------
def generate_visualizations(df):
    charts = {}
    if df.empty:
        return charts

    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.strftime('%b %Y')

    debit_df = df[df['Amount'] < 0].copy()
    debit_df['Amount'] = debit_df['Amount'].abs()

    charts['category_pie'] = px.pie(debit_df, names='Category', values='Amount', title="Spending by Category")
    charts['monthly_spending'] = px.bar(debit_df.groupby('Month')['Amount'].sum().reset_index(),
                                        x='Month', y='Amount', title="Monthly Spending")
    charts['top_expenses'] = px.bar(debit_df.nlargest(10, 'Amount'), x='Description', y='Amount',
                                    title="Top 10 Expenses", color='Category')
    return charts

# ---------------- Streamlit App ----------------
st.set_page_config(page_title="💸 AI UPI Financial Analyzer", layout="wide")

st.title("💰 AI-Powered Personal UPI & Bank Statement Analyzer")
st.caption("Analyze Paytm and PhonePe statements using Google Gemini AI")

gemini_api_key = st.sidebar.text_input("🔑 Enter Gemini API Key", type="password")
uploaded_file = st.sidebar.file_uploader("📄 Upload Statement PDF", type=["pdf"])

if uploaded_file and gemini_api_key:
    with st.spinner("Extracting text from PDF..."):
        text = extract_text_from_pdf(uploaded_file)

    if text:
        source = detect_statement_source(text)
        st.info(f"📘 Detected Source: **{source}**")

        if source == "PhonePe":
            transactions = parse_phonepe_data(text)
        elif source == "Paytm":
            transactions = parse_paytm_data(text)
        else:
            st.error("❌ Unsupported statement type. Upload Paytm or PhonePe statement.")
            st.stop()

        df = pd.DataFrame(transactions)
        st.dataframe(df.head(20), use_container_width=True)

        # Visuals
        charts = generate_visualizations(df)
        st.subheader("📊 Spending Overview")
        if 'category_pie' in charts:
            st.plotly_chart(charts['category_pie'], use_container_width=True)
        if 'monthly_spending' in charts:
            st.plotly_chart(charts['monthly_spending'], use_container_width=True)
        if 'top_expenses' in charts:
            st.plotly_chart(charts['top_expenses'], use_container_width=True)

        # AI Insights
        with st.spinner("🧠 Generating AI Insights..."):
            insights = analyze_financial_data(text, gemini_api_key)
        st.markdown(insights)

        st.download_button("📥 Download AI Report", insights, file_name="financial_report.txt")
    else:
        st.error("❌ Failed to extract text. Please upload a valid PDF.")
else:
    st.warning("👆 Upload a statement and enter your Gemini API key to start analysis.")

