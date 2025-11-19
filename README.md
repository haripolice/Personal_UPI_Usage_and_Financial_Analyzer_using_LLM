---
title: Personal Financial Analyser
emoji: 📊
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---

# 💰 Personal UPI Usage and Financial Analyzer using LLMs

This project is an **AI-powered financial analyzer** that processes UPI transaction PDFs (from Paytm, GPay, PhonePe, etc.) to extract, analyze, and provide **personalized financial insights** using **Google Gemini LLM**.

## 🚀 Features
- 📂 **PDF Parsing:** Extracts text and data from UPI transaction statements.
- 💡 **AI Insights:** Uses Gemini to analyze spending patterns, unnecessary expenses, and provide financial advice.
- 📊 **Interactive Dashboard:** Built with Streamlit for an intuitive user experience.
- 🔒 **Secure Local Processing:** All data is processed locally before sending for analysis.

## 🧠 Tech Stack
- **Frontend/UI:** Streamlit  
- **Backend:** Python  
- **AI Model:** Google Gemini API  
- **Libraries:** PyPDF2, Pandas, Plotly  

## 🧰 Installation
1. Clone the Repository  
```bash
git clone https://github.com/<your-username>/personal-upi-analyzer.git
cd personal-upi-analyzer
```
2. Install Dependencies  
```bash
pip install -r requirements.txt
```
3. Add Your Gemini API Key  
In `app.py`, replace the placeholder with your Gemini API key.
```python
GEMINI_API_KEY = "your_api_key_here"
```
4. Run the App  
```bash
streamlit run app.py
```

## 📈 Example Use Case
1. Upload your **Paytm/GPay/PhonePe** transaction PDF.  
2. The system extracts and analyzes all transactions.  
3. View detailed insights including:
   - Monthly income & expenses  
   - Category-wise spending breakdown  
   - Savings percentage  
   - Personalized recommendations  

## 🧪 Evaluation Metrics
- ✅ Accuracy of PDF data extraction  
- 💬 Relevance of AI insights  
- 📉 Time efficiency of processing  
- 🤝 User satisfaction  

