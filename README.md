# Smart Resume Screening System

An AI-powered resume screening API that matches resumes against job descriptions using TF-IDF and skill-based matching.

## Features
- Resume parsing for PDF, DOCX, and TXT files
- Skill extraction from resume content
- TF-IDF + cosine similarity text matching
- Weighted score output with matched and missing skills
- FastAPI endpoint with Swagger docs

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Run the API
```bash
python app/main.py
```

The API will be available at http://127.0.0.1:8000.

## API Usage
Send a multipart form request to /screen-resumes with:
- jobtitle
- jobdescription
- requiredskills (comma-separated)
- resumes (one or more files)

Example:
```bash
curl -X POST "http://127.0.0.1:8000/screen-resumes" \
  -F "jobtitle=Python Developer" \
  -F "jobdescription=We are looking for a Python developer with FastAPI and SQL experience." \
  -F "requiredskills=Python, FastAPI, SQL, Git" \
  -F "resumes=@sample_resumes/resume1.txt"
```