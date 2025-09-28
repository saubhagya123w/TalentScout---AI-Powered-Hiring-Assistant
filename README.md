# TalentScout — AI-Powered Hiring Assistant

  An **LLM-powered intelligent hiring assistant** built with **Python** and **Streamlit**,  
  designed to streamline candidate screening by collecting structured information  
  and generating technical interview questions automatically.  

  ---

  ## 🚀 Project Overview
  TalentScout acts as a **virtual recruiter assistant** that:
  - Greets and guides candidates in a friendly conversational flow
  - Collects structured candidate information (name, email, experience, tech stack, role preferences)
  - Generates **3–5 technical screening questions per technology** (OpenAI or offline rule-based fallback)
  - Maintains conversation context with `st.session_state`
  - Stores anonymized candidate data as JSON locally
  - Runs fully offline with rule-based fallback

  ---

  ## 🛠 Tech Stack
  - **Frontend/UI**: Streamlit  
  - **Backend**: Python  
  - **LLM Integration**: OpenAI API (optional), Rule-based fallback  
  - **Prompt Engineering**: Custom structured prompts in `prompts.py`  
  - **Data Handling**: Local JSON storage (`utils_storage.py`)  
  - **Experimentation**: Jupyter notebooks (for dev), `.py` files (for deployment)  

  ---

  ## 📂 Project Structure
TalentScout/
├─ app.py # Streamlit app entry point
├─ chatbot_logic.py # LLM wrapper + chatbot logic
├─ prompts.py # Prompt templates
├─ utils_storage.py # Local storage helpers
├─ generate_dummy_data.py # Dummy candidate generator
├─ requirements.txt # Dependencies
├─ .env.example # Environment variable template
└─ README.md # Documentation

yaml
Copy code

---

## ✨ Key Features
✅ Conversational Candidate Intake — structured candidate details  
✅ Dynamic Question Generation — 3–5 screening questions per tech stack  
✅ LLM Wrapper — modular integration (OpenAI / fallback)  
✅ Rule-Based Mode — works offline without APIs  
✅ Session Management — conversation context via `st.session_state`  
✅ Local Data Storage — anonymized JSON export  
✅ Dummy Candidate Generator — instant testing with synthetic data  

---

## 📸 Demo Workflow
1. Candidate fills in form (name, email, experience, skills)  
2. Chatbot greets and asks about tech stack  
3. Generates technical questions like:  
   - [Python] Explain the difference between a list and a tuple  
   - [SQL] Write a query to find duplicate rows  
   - [React] What are React hooks and why were they introduced?  
4. Candidate can exit gracefully (`exit`, `quit`, `done`)  
5. Candidate record saved locally as anonymized JSON  

---

## 🧑‍💻 Installation & Setup
```bash
git clone <your-repo-url> TalentScout
cd TalentScout

# Create virtual environment
python -m venv sub1
sub1\Scripts\activate       # Windows
source sub1/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
🏗 File Descriptions
app.py — Streamlit interface; handles user chat flow and form submission

chatbot_logic.py — Chatbot engine with LLM wrapper + fallback

prompts.py — Prompt templates for structured question generation

utils_storage.py — Save anonymized candidate JSON locally

generate_dummy_data.py — Create synthetic candidate profiles for testing

📊 Skills & Concepts Demonstrated
AI/ML Engineering: LLM integration, Prompt Engineering, Rule-based NLP

Software Engineering: Python modular design, session management, JSON handling

Tools: Streamlit, OpenAI API (optional), Jupyter notebooks for experimentation

