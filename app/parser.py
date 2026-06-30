import re
from pathlib import Path
from typing import Optional

import pdfplumber
from docx import Document

SKILLPATTERNS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "go",
    "rust",
    "ruby",
    "react",
    "angular",
    "vue",
    "node.js",
    "django",
    "flask",
    "fastapi",
    "spring",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",
    "elasticsearch",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "terraform",
    "jenkins",
    "git",
    "linux",
    "rest api",
    "graphql",
    "microservices",
    "machine learning",
    "deep learning",
    "nlp",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "spark",
    "hadoop",
    "kafka",
    "airflow",
    "html",
    "css",
    "sass",
    "tailwind",
    "bootstrap",
    "agile",
    "scrum",
    "ci/cd",
    "devops",
    "jira",
]


def extracttextfrompdf(filepath: str) -> str:
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            pagetext = page.extract_text()
            if pagetext:
                text += pagetext + "\n"
    return text


def extracttextfromdocx(filepath: str) -> str:
    doc = Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])


def extracttextfromtxt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as handle:
        return handle.read()


def extracttext(filepath: str) -> str:
    path = Path(filepath)
    extension = path.suffix.lower()

    extractors = {
        ".pdf": extracttextfrompdf,
        ".docx": extracttextfromdocx,
        ".txt": extracttextfromtxt,
    }

    extractor = extractors.get(extension)
    if not extractor:
        raise ValueError(f"Unsupported file format: {extension}")

    return extractor(filepath)


def extractskills(text: str) -> list[str]:
    textlower = text.lower()
    foundskills: list[str] = []

    for skill in SKILLPATTERNS:
        escaped = re.escape(skill).replace(r"\ ", r"\s+")
        pattern = rf"(?<!\w){escaped}(?!\w)"
        if re.search(pattern, textlower):
            foundskills.append(skill)

    return list(dict.fromkeys(foundskills))


def extractexperienceyears(text: str) -> Optional[int]:
    patterns = [
        r"(\d+)\+?\s(?:years?|yrs?)\s(?:of)?\s(?:experience|exp)",
        r"experience\s*(?:for)?\s*(\d+)\+?\s(?:years?|yrs?)",
        r"(\d+)\+?\s(?:years?|yrs?)\s(?:in|of)\s(?:software|development|programming)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))

    return None


def parseresume(filepath: str) -> dict:
    text = extracttext(filepath)
    return {
        "text": text,
        "skills": extractskills(text),
        "experienceyears": extractexperienceyears(text),
    }
