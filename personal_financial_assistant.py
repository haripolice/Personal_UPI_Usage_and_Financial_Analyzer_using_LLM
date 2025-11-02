import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import google.generativeai as genai
from datetime import datetime

# ===========================
# 🔐 SET YOUR GEMINI API KEY
# ===========================
GOOGLE_API_KEY = "AIzaSyAQlEKIu-QbsZnOIxK1Yaw1JICgWSN9G7o"
genai.configure(api_key=GOOGLE_API_KEY)

# ------------------------------
# PDF Processing
# ------------------------------
def extract_text_from_pdf(uploaded_file):
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        st.error(f"Failed to read PDF: {str(e)}")
        return None

# ------------------------------
# Transaction Parsing
# ------------------------------
def parse_transactions(text):
    if not text:
        return pd.DataFrame()

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    transactions = []
    current_trans = {}

    for line in lines:
        date_match = re.match(r'(\d{2}[/-]\d{2}[/-]\d{4})|(\d{2} \w{3} \d{4})', line)
        if date_match:
            if current_trans:
                transactions.append(current_trans)
            current_trans = {
                'Date': date_match.group(),
                'Description': line[len(date_match.group()):].strip(),
                'Amount': None
            }
        elif current_trans:
            amount_match = re.search(r'(?:INR|Rs|₹)\s*([\d,]+\.\d{2})', line)
            if amount_match:
                current_trans['Amount'] = float(amount_match.group(1).replace(',', ''))
            else:
                current_trans['Description'] += " " + line

    if current_trans:
        transactions.append(current_trans)

    return pd.DataFrame(transactions)

# ------------------------------
# Categorization
# ------------------------------
DEFAULT_CATEGORIES = {
    'Food': ['swiggy', 'zomato', 'food', 'zepto', 'bigbasket', 'dominos', 'pizza', 'kfc', 'mcdonalds', 'burger king', 'starbucks'],
    'Travel': ['uber', 'ola', 'travel', 'rapido', 'suncityfuels', 'aswini automobiles'],
    'Shopping': ['amazon', 'flipkart', 'meesho', 'myntra', 'shopping', 'v mart', 'dmart', 'croma', 'reliance digital'],
    'Entertainment': ['netflix', 'spotify', 'hotstar', 'cinemas', 'pvr', 'inox'],
    'Bills': ['electricity', 'water', 'gas', 'bills', 'paytm', 'phonepe', 'lic', 'google india'],
    'Health': ['pharmacy', 'doctor', 'health', 'medicine'],
    'Friends & Family': ['gift', 'friends', 'family'],
    'Salary': ['salary', 'income', 'pay'],
    'Others': []
}

def categorize_transactions(df, categories):
    if df.empty:
        return df

    def get_category(description):
        desc = description.lower()
        for category, keywords in categories.items():
            if any(keyword in desc for keyword in keywords):
                return category
        return "Others"

    df['Category'] = df['Description'].apply(get_category)
    return df

# ------------------------------
# Gemini AI Recommendations
# ------------------------------
def generate_gemini_recommendations(df):
    if df.empty:
        return "No transactions to analyze."

    try:
        # Use a sample to reduce input tokens
        sample_df = df.sample(min(len(df), 10))
        sample_csv = sample_df.to_csv(index=False)

        model = genai.GenerativeModel("models/gemini-1.5-flash")
        prompt = f"""
Analyze the following bank transaction data and provide:

- A brief spending summary
- 2 interesting insights
- 2 short budgeting tips

Data (CSV):
{sample_csv}
"""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error generating AI insights: {e}"


# ------------------------------
# Main App
# ------------------------------
def main():
    st.set_page_config(page_title="UPI Analyzer Pro", layout="wide")
    st.title("📊 UPI Analyzer Pro with Smart Insights")

    uploaded_file = st.file_uploader("Upload UPI Statement PDF", type="pdf")

    if uploaded_file:
        with st.spinner("Extracting text..."):
            raw_text = extract_text_from_pdf(uploaded_file)

        if not raw_text:
            return

        with st.spinner("Parsing transactions..."):
            df = parse_transactions(raw_text)

        if df.empty:
            st.error("No transactions found. Please check your PDF.")
            return

        with st.spinner("Categorizing..."):
            categorized_df = categorize_transactions(df, DEFAULT_CATEGORIES)
            categorized_df['Date'] = pd.to_datetime(categorized_df['Date'], dayfirst=True, errors='coerce')
            categorized_df = categorized_df.dropna(subset=['Date'])

        st.success(f"Processed {len(categorized_df)} transactions!")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spent", f"₹{categorized_df['Amount'].sum():,.2f}")
        col2.metric("Transactions", len(categorized_df))
        col3.metric("Period", f"{categorized_df['Date'].min().strftime('%d %b')} to {categorized_df['Date'].max().strftime('%d %b %Y')}")

        tab1, tab2 = st.tabs(["📄 Transactions", "📈 Insights"])

        with tab1:
            st.write("### Transaction History")
            st.dataframe(categorized_df.sort_values(by='Date', ascending=False))

        with tab2:
            st.write("### Spending by Month")
            monthly_chart = categorized_df.groupby(pd.to_datetime(categorized_df['Date']).dt.strftime('%b %Y'))['Amount'].sum()
            st.bar_chart(monthly_chart)

            st.write("### Category-wise Spending")
            category_chart = categorized_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
            st.bar_chart(category_chart)

            st.write("### 🤖 AI-Powered Financial Advice")
            with st.spinner("Generating AI insights using Gemini..."):
                insights = generate_gemini_recommendations(categorized_df)
            st.markdown(insights)

if __name__ == "__main__":
    main()
