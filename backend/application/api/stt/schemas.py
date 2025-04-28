from pydantic import BaseModel


class UploadAudioResponseSchema(BaseModel):
    text: str
