from typing import Any

from pydantic import Field

from .base import BaseMaxObject


class Folder(BaseMaxObject):
    source_id: int = 0
    include: list[int] = Field(default_factory=list)
    options: list[Any] = Field(default_factory=list)
    update_time: int = 0
    id: str = ""
    filters: list[Any] = Field(default_factory=list)
    title: str = ""


class FolderUpdate(BaseMaxObject):
    folders_order: list[str] = Field(default_factory=list)
    folder: Folder | None = None
    folder_sync: int = 0


class FolderList(BaseMaxObject):
    folders_order: list[str] = Field(default_factory=list)
    folders: list[Folder] = Field(default_factory=list)
    all_filter_exclude_folders: list[Any] = Field(default_factory=list)
    folder_sync: int = 0
