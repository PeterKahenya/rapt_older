from pydantic import BaseModel,UUID4
from typing import List,Optional
from datetime import datetime


class ModelBase(BaseModel):
    id: UUID4

    model_config = {
        "from_attributes": True
    }

class ModelInDBBase(ModelBase):
    created_at: datetime
    updated_at: datetime | None

# client app schema
class ClientAppCreate(BaseModel):
    name: str
    description: str


class ClientAppUpdate(BaseModel):
    name: str | None
    description: str | None

class ClientAppInDBBase(ModelInDBBase):
    name: str
    description: str
    client_id: str
    client_secret: str

# content type schema
class ContentTypeCreate(BaseModel):
    content: str

class ContentTypeUpdate(ContentTypeCreate):
    pass

class ContentTypeInDBBase(ModelInDBBase):
    content: str



# permission schema
class PermissionCreate(BaseModel):
    name: str
    codename: str
    content_type_id: UUID4

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    codename: Optional[str] = None
    content_type_id: Optional[UUID4] = None

class PermissionInDBBase(ModelInDBBase):
    name: str
    codename: str
    content_type: ContentTypeInDBBase


# role schema
class RoleCreate(BaseModel):
    name: str
    description: str

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: List[ModelBase] | None

class RoleInDBBase(ModelInDBBase):
    name: str
    description: str
    permissions: List[PermissionInDBBase] | None


# user schema
class UserCreate(BaseModel):
    name: str
    phone: str

class UserContactCreate(BaseModel):
    name: str
    phone: str

class UserContact(BaseModel):
    name: str
    phone: str
    is_active: bool
    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    phone_verification_code: Optional[str] = None
    phone_verification_code_expiry_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    last_seen: Optional[datetime] = None
    contacts: List[UserContact] | None
    roles: List[ModelBase] | None

class UserInDBBase(ModelInDBBase):
    name: str
    phone: str
    phone_verification_code_expiry_at: datetime | None
    is_active: bool
    is_superuser: bool
    is_verified: bool
    last_seen: datetime | None
    contacts: List[UserContact] | None
    roles: List[RoleInDBBase] | None

# chatroom schema
class ChatRoomCreate(BaseModel):
    fcm_room_id: str
    socket_room_id: str
    members: Optional[List[ModelBase]] = None

class ChatRoomUpdate(BaseModel):
    fcm_room_id: Optional[str] = None
    socket_room_id: Optional[str] = None
    members: List[ModelBase] | None

# media schema
class MediaCreate(BaseModel):
    link: str
    file_type: str

class MediaUpdate(BaseModel):
    link: Optional[str] = None
    file_type: Optional[str] = None

class MediaInDBBase(ModelInDBBase):
    link: str
    file_type: str

# chat schema
class ChatCreate(BaseModel):
    message: str
    media: Optional[List[ModelBase]] = None
    sender: ModelBase | None
    room: ModelBase

class ChatUpdate(BaseModel):
    message: Optional[str] = None
    media: List[ModelBase] | None
    is_read: Optional[bool] = None

class ChatInDBBase(ModelInDBBase):
    message: str
    is_read: bool
    sender: UserInDBBase
    room: ModelBase
    media: List[MediaInDBBase] | None

# chatroomindb schema
class ChatRoomInDBBase(ModelInDBBase):
    fcm_room_id: str
    socket_room_id: str
    members: List[UserInDBBase] | None
    room_chats: List[ChatInDBBase] | None


# group schema
class GroupCreate(BaseModel):
    name: str
    description: str
    chatroom: ModelBase

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chatroom: Optional[ModelBase] = None

class GroupInDBBase(ModelInDBBase):
    name: str
    description: str
    chatroom: ChatRoomInDBBase










