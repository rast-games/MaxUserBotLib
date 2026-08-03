import uuid
from collections.abc import Sequence, Coroutine, Callable
from typing import cast, Any

from .....models import Contact, PhotoAttachment, Profile, FolderUpdate, FolderList
from .....protocol.envelope import Envelope
from ..payloads.shared import CamelCaseModel
from ..payloads.responses import (
    GetContactResponse,
    ResponseWithUrl,
    ProfileContainsResponse,
)
from ..methods.immutable import (
    GetGeneralInfoAboutMemberMethod,
    CreateCellForProfilePhotoMethod,
    ChangeProfileMethod,
    CreateFolderMethod,
    GetFoldersMethod,
    UpdateFolderMethod,
    DeleteFoldersMethod,
)
from ..payloads.models import (
    PhotoMappingModel,
    FolderUpdateMappingModel,
    FolderListMappingModel,
)
from ..translate.ToDTO import (
    FILE_OPCODES,
    FALLBACK_FILE_OPCODE,
    translate_models,
    upload_file,
)
from ..constants import Opcode

from .MixinProtocol import MixinProtocol


class UserMixin(MixinProtocol):
    async def get_member_by_id(self, member_id: int | list[int]) -> Sequence[Contact]:
        contact_ids: list[int]
        if isinstance(member_id, int):
            contact_ids = [member_id]
        elif isinstance(member_id, list):
            contact_ids = member_id
        else:
            raise TypeError("member_id must be int or list[int]")

        response_envelope = await self.send(
            method=GetGeneralInfoAboutMemberMethod(
                contact_ids=contact_ids,
            )
        )

        response = GetContactResponse(**response_envelope.payload)

        contacts = [
            translate_models(mapping_contact) for mapping_contact in response.contacts
        ]

        return [contact for contact in contacts if isinstance(contact, Contact)]

        # return cast(list[BaseMaxObject], contacts)

    async def _create_cell_for_profile_photo(
        self,
        count: int = 1,
        profile: bool = True,
    ) -> dict[str, Any]:
        response = await self.send(
            method=CreateCellForProfilePhotoMethod(
                type_of_file_opcode=Opcode.CREATE_PHOTO,
                count=count,
                profile=profile,
            )
        )

        payload = ResponseWithUrl(**response.payload).model_dump(exclude_none=True)

        return payload

    async def upload_profile_photo(
        self,
        data: bytes | None,
        count: int = 1,
        file_name: str | None = None,
        uploaded: bool = False,
        **kwargs: Any,
    ) -> list[PhotoMappingModel]:
        payload = {}
        if not uploaded:
            payload = await self._create_cell_for_profile_photo(
                count=count,
                profile=True,
            )

        uploaded_file = await upload_file(
            data=data,
            typeof=PhotoAttachment,
            file_name=file_name,
            uploaded=uploaded,
            **payload,
            **kwargs,
        )

        return cast(list[PhotoMappingModel], uploaded_file)

    async def change_profile(
        self,
        first_name: str,
        last_name: str | None = None,
        description: str | None = None,
        photo: bytes | None = None,
        file_name: str | None = None,
        photo_token: str | None = None,
    ) -> Profile:
        if self.max_api is None:
            raise RuntimeError("max_api not bounded to mapper")

        if photo is not None:
            if photo_token:
                self._logger.warning(
                    "photo_token argument was provided but will be overridden by "
                    "the uploaded photo token"
                )
            attach = await self.upload_profile_photo(
                data=photo,
                file_name=file_name,
            )
            photo_token = attach[0].photo_token
        response = await self.send(
            method=ChangeProfileMethod(
                first_name=first_name,
                last_name=last_name,
                description=description,
                photo_token=photo_token,
            )
        )

        mapped_profile = ProfileContainsResponse(**response.payload)

        profile = cast(Profile, translate_models(mapped_profile))
        self.max_api.me = profile
        return profile

    async def create_folder(
        self,
        title: str,
        chat_include: list[int],
        filters: list[Any] | None = None,
        folder_id: str | None = None,
    ) -> FolderUpdate:
        self._logger.info("creating folder")

        response = await self.send(
            method=CreateFolderMethod(
                id=folder_id or str(uuid.uuid4()),
                title=title,
                include=chat_include,
                filters=filters or [],
            )
        )

        folder_update_mapped = FolderUpdateMappingModel(**response.payload)
        folder_update = cast(FolderUpdate, translate_models(folder_update_mapped))
        return folder_update

    async def get_folders(self, folder_sync: int = 0) -> FolderList:
        self._logger.info("fetching folders")
        response = await self.send(
            method=GetFoldersMethod(
                folder_sync=folder_sync,
            )
        )
        mapped_folder_list = FolderListMappingModel(**response.payload)
        folder_list = cast(FolderList, translate_models(mapped_folder_list))
        return folder_list

    async def update_folder(
        self,
        folder_id: str,
        title: str,
        chat_include: list[int] | None = None,
        filters: list[Any] | None = None,
        options: list[Any] | None = None,
    ) -> FolderUpdate:
        self._logger.info("updating folder")
        response = await self.send(
            method=UpdateFolderMethod(
                id=folder_id,
                title=title,
                include=chat_include or [],
                filters=filters or [],
                options=options or [],
            )
        )
        folder_update_mapped = FolderUpdateMappingModel(**response.payload)
        folder_update = cast(FolderUpdate, translate_models(folder_update_mapped))
        return folder_update

    async def delete_folders(self, folder_ids: list[str]) -> FolderUpdate:
        response = await self.send(
            method=DeleteFoldersMethod(
                folder_ids=folder_ids,
            )
        )
        folder_update_mapped = FolderUpdateMappingModel(**response.payload)
        folder_update = cast(FolderUpdate, translate_models(folder_update_mapped))
        return folder_update
