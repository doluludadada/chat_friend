from pydantic import BaseModel


class LineMessage(BaseModel):
    type: str
    id: str
    text: str | None = None


class LineSource(BaseModel):
    type: str
    userId: str


class LineEvent(BaseModel):
    type: str
    message: LineMessage | None = None
    source: LineSource


class LineWebhookPayload(BaseModel):
    destination: str
    events: list[LineEvent] = []
