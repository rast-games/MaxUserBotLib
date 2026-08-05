from pydantic import BaseModel


class BaseFileAttachment(BaseModel):
    pass


class VideoAttachment(BaseFileAttachment):
    pass


class VoiceAttachment(BaseFileAttachment):
    pass


class VideoNoteAttachment(BaseFileAttachment):
    pass


class PhotoAttachment(BaseFileAttachment):
    pass


class FileAttachment(BaseFileAttachment):
    pass


class ShareAttachment(BaseFileAttachment):
    pass


class ControlAttachment(BaseFileAttachment):
    pass
