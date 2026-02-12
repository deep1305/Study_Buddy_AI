from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator


def _clean_text(v: object) -> str:
    """
    Make LLM/tool output safe for string fields.

    - If a dict is provided (e.g., {"description": "..."}), extract description.
    - Always return a stripped string.
    """
    if isinstance(v, dict):
        v = v.get("description", str(v))
    return str(v).strip()

class MCQQuestion(BaseModel):

    question: str = Field(description="The question to be answered")

    options: list[str] = Field(description="List of 4 options for the question")

    # Return the correct answer as text (e.g., "Paris").
    correct_answer: str = Field(description="Correct answer text (must be one of the options)")

    @field_validator("question", mode="before")
    @classmethod
    def clean_question(cls, v: object) -> str:
        return _clean_text(v)

    @field_validator("options", mode="before")
    @classmethod
    def clean_options(cls, v: object) -> list[str]:
        # Ensure list[str] and strip each option.
        if v is None:
            return []
        if not isinstance(v, (list, tuple)):
            raise TypeError("options must be a list of strings")
        return [_clean_text(opt) for opt in v]

    @field_validator("correct_answer", mode="before")
    @classmethod
    def clean_correct_answer(cls, v: object) -> str:
        return _clean_text(v)

    @property
    def correct_option(self) -> int:
        """
        Convenience: 0-based index of the correct answer in `options`.
        """
        return self.options.index(self.correct_answer)

    @model_validator(mode="after")
    def validate_mcq(self) -> "MCQQuestion":
        if not self.question:
            raise ValueError("question cannot be empty")

        if len(self.options) != 4:
            raise ValueError("options must contain exactly 4 items")

        if any(not opt for opt in self.options):
            raise ValueError("options cannot contain empty strings")

        if not self.correct_answer:
            raise ValueError("correct_answer cannot be empty")

        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must be one of the options")

        return self

class FillBlankQuestion(BaseModel):
    question: str = Field(description="The question to be answered with a blank space for the answer")
    answer: str = Field(description="The correct word or phrase for the blank space in the question")

    @field_validator("question", mode="before")
    @classmethod
    def clean_question(cls, v: object) -> str:
        return _clean_text(v)

    @field_validator("answer", mode="before")
    @classmethod
    def clean_answer(cls, v: object) -> str:
        return _clean_text(v)

    @model_validator(mode="after")
    def validate_fill_blank(self) -> "FillBlankQuestion":
        if not self.question:
            raise ValueError("question cannot be empty")
        if not self.answer:
            raise ValueError("answer cannot be empty")
        return self

