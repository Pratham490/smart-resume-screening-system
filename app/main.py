import os
import sys
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from .matcher import matchresumetojd
    from .models import JobDescription, ResumeResult, ScreeningResponse
    from .parser import parseresume
except ImportError:  # pragma: no cover - handles running the file directly
    from app.matcher import matchresumetojd
    from app.models import JobDescription, ResumeResult, ScreeningResponse
    from app.parser import parseresume

app = FastAPI(
    title="Smart Resume Screening API",
    description="AI-powered resume screening system using TF-IDF and skill matching",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Smart Resume Screening API",
        "docs": "/docs",
        "endpoint": "POST /screen-resumes",
    }


@app.post("/screen-resumes", response_model=ScreeningResponse)
async def screenresumes(
    jobtitle: Annotated[str, Form(description="Job title")],
    jobdescription: Annotated[str, Form(description="Full job description text")],
    requiredskills: Annotated[str, Form(description="Comma-separated list of required skills")],
    resumes: Annotated[list[UploadFile], File(description="Resume files (PDF, DOCX, or TXT)")],
):
    skillslist = [skill.strip() for skill in requiredskills.split(",") if skill.strip()]

    if not skillslist:
        raise HTTPException(status_code=400, detail="At least one required skill must be provided")

    if not resumes:
        raise HTTPException(status_code=400, detail="At least one resume must be uploaded")

    results = []

    for resumefile in resumes:
        filename = resumefile.filename or "unknown"
        extension = os.path.splitext(filename)[1].lower()

        if extension not in [".pdf", ".docx", ".txt"]:
            results.append(
                ResumeResult(
                    filename=filename,
                    matchscore=0,
                    matchedskills=[],
                    missingskills=skillslist,
                    explanation=f"Unsupported file format: {extension}. Supported: PDF, DOCX, TXT.",
                )
            )
            continue

        tmppath = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
                content = await resumefile.read()
                tmp.write(content)
                tmppath = tmp.name

            parsed = parseresume(tmppath)
            matchresult = matchresumetojd(
                resumetext=parsed["text"],
                resumeskills=parsed["skills"],
                jdtext=jobdescription,
                requiredskills=skillslist,
            )

            results.append(
                ResumeResult(
                    filename=filename,
                    matchscore=matchresult["matchscore"],
                    matchedskills=matchresult["matchedskills"],
                    missingskills=matchresult["missingskills"],
                    explanation=matchresult["explanation"],
                )
            )
        except Exception as exc:
            results.append(
                ResumeResult(
                    filename=filename,
                    matchscore=0,
                    matchedskills=[],
                    missingskills=skillslist,
                    explanation=f"Error processing file: {exc}",
                )
            )
        finally:
            if tmppath and os.path.exists(tmppath):
                os.unlink(tmppath)

    results.sort(key=lambda item: item.matchscore, reverse=True)

    return ScreeningResponse(
        jobtitle=jobtitle,
        totalresumes=len(results),
        results=results,
    )


@app.get("/health")
async def healthcheck():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
