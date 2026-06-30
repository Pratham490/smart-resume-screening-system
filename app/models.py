from typing import List

from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Full job description text")
    requiredskills: List[str] = Field(..., description="List of required skills")


class ResumeResult(BaseModel):
    filename: str
    matchscore: int = Field(..., ge=0, le=100)
    matchedskills: List[str]
    missingskills: List[str]
    explanation: str


class ScreeningResponse(BaseModel):
    jobtitle: str
    totalresumes: int
    results: List[ResumeResult]
