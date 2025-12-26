from pydantic import BaseModel, Field
from typing import List, Optional


class ExperienceItem(BaseModel):
    company: str = Field(..., description="Company or project name")
    role: Optional[str] = Field(None, description="Role/title")
    start: Optional[str] = Field(None, description="Start date (free-form)")
    end: Optional[str] = Field(None, description="End date (free-form)")
    highlights: List[str] = Field(default_factory=list, description="Key bullet points")


class DocumentSummary(BaseModel):
    refusal: bool = False
    refusal_reason: Optional[str] = None
    candidate_name: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None

    summary_points: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)

    experience: List[ExperienceItem] = Field(default_factory=list)
