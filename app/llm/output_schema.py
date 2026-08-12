from __future__ import annotations

from pydantic import BaseModel, Field

class LLMReportSchema(BaseModel):
 summary: str = Field(..., min_length=1)
 top_issues: list[str] = Field(default_factory=list)
 overall_assessment: str = Field(..., min_length=1)
 recommended_actions: list[str] = Field(default_factory=list)