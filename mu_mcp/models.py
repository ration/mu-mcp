from pydantic import BaseModel, ConfigDict, Field


class Address(BaseModel):
    name: str = ""
    email: str


class Email(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    subject: str
    from_: list[Address] = Field(alias="from")
    to: list[Address] = Field(default_factory=list)
    cc: list[Address] = Field(default_factory=list)
    date: str  # ISO 8601 UTC
    path: str
    message_id: str | None = Field(alias="message-id", default=None)
    size: int = 0
    flags: list[str] = Field(default_factory=list)
    maildir: str = ""
    priority: str = "normal"


