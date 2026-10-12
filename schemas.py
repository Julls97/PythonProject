from pydantic import BaseModel, ConfigDict, Field


class ExtractedTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=0, max_length=5000)
    assignee_name: str | None = Field(default=None, max_length=255)
    due_phrase: str | None = Field(default=None, max_length=255)


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: list[ExtractedTask] = Field(max_length=10)
