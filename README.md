---
title: Resume Intelligence AI
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# AI Resume Intelligence Platform

An advanced AI-powered resume analysis platform built with **Django** and **Google Gemini 2.5 Flash**.  
Upload your resume and get instant AI-driven insights — summaries, strengths, weaknesses, job title suggestions, and JD gap analysis.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Smart Summary** | AI-generated overview of qualifications, skills, and experience |
| 💪 **Strength Analysis** | Identify your competitive advantages |
| 🎯 **Weakness Audit** | Get actionable suggestions to improve your resume |
| 💼 **Job Matching** | AI-recommended job titles based on your profile |
| 📊 **JD Gap Analysis** | Compare your resume against any job description with match score |
| 🔗 **LinkedIn Scraper** | Automatically scrape relevant job listings from LinkedIn |
| 📥 **PDF Export** | Download a styled PDF report of your analysis |
| 📊 **Skills Radar Chart** | Interactive Plotly visualization of your skill proficiencies |
| 📄 **Multi-Format Upload** | Support for PDF, DOCX, and TXT files |

---

## 🛠️ Tech Stack

- **Backend:** Django 4.2, Python 3.11
- **AI/ML:** Google Gemini 2.5 Flash, LangChain
- **Data Viz:** Plotly.js
- **Scraping:** Selenium + Chrome WebDriver
- **PDF Export:** ReportLab
- **Deployment:** Docker → Hugging Face Spaces
- **Styling:** Custom CSS (Glassmorphism Dark Theme)

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-intelligence.git
cd ai-resume-intelligence
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Start the server
```bash
python manage.py runserver
```

### 6. Open in browser
```
http://127.0.0.1:8000
```

---

## 🔑 API Key

You need a **Google Gemini API Key** to use this application.  
Get one for free at: [https://aistudio.google.com/](https://aistudio.google.com/)

---

## 🐳 Docker Deployment (Hugging Face Spaces)

1. Create a new Hugging Face Space → select **Docker** SDK
2. Add a **Repository Secret** named `GEMINI_API_KEY`
3. Push this code to the Space repository
4. The app will auto-build and deploy on port `7860`

---

## 📁 Project Structure

```
├── core/                   # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── analyzer/               # Main Django app
│   ├── views.py            # API endpoints
│   ├── forms.py            # Django forms
│   ├── urls.py
│   └── utils/
│       ├── gemini_ai.py    # Gemini AI integration
│       ├── pdf_parser.py   # Multi-format text extraction
│       ├── charts.py       # Plotly chart data generation
│       ├── pdf_export.py   # ReportLab PDF reports
│       └── scraper.py      # LinkedIn Selenium scraper
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── requirements.txt
├── Dockerfile
└── manage.py
```

---

## 📧 Contact

For questions or feedback, feel free to reach out!

---

## 📄 License

This project is licensed under the MIT License.
