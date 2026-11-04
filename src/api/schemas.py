
from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    comments: list[str] = Field(
        min_length=1,
        max_length=100,
        description="Liste de commentaires à analyser"
    )

    @field_validator("comments")
    @classmethod
    def validate_comments(cls, comments):
        comments = [comment.strip() for comment in comments]

        if any(not comment for comment in comments):
            raise ValueError("Les commentaires ne doivent pas être vides.")

        if any(len(comment) > 5000 for comment in comments):
            raise ValueError("Un commentaire ne doit pas dépasser 5000 caractères.")

        return comments
