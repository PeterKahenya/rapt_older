from typing import List
import uuid
from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy import Column,Uuid,String,Boolean,DateTime,ForeignKey,Table
from sqlalchemy.orm import relationship,backref
from sqlalchemy.orm import declarative_base,Session
from config import settings,logger
from utils import generate_random_string, generate_client_id, generate_client_secret

Model = declarative_base()

contacts_association = Table(
    'contacts',
    Model.metadata,
    Column('user_id', Uuid, ForeignKey('users.id'), primary_key=True),
    Column('contact_id', Uuid, ForeignKey('users.id'), primary_key=True)
)

chatroom_members_association = Table(
    'chatroom_members',
    Model.metadata,
    Column('user_id', Uuid, ForeignKey('users.id'), primary_key=True),
    Column('chatroom_id', Uuid, ForeignKey('chatrooms.id'), primary_key=True)
)

role_permissions_association = Table(
    'role_permissions',
    Model.metadata,
    Column('role_id', Uuid, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Uuid, ForeignKey('permissions.id'), primary_key=True)
)

user_roles_association = Table(
    'user_roles',
    Model.metadata,
    Column('user_id', Uuid, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Uuid, ForeignKey('roles.id'), primary_key=True)
)

class User(Model):
    __tablename__ = "users"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    name = Column(String(50))
    phone = Column(String(12),unique=True)
    is_active = Column(Boolean,default=False)
    is_superuser = Column(Boolean,default=False)
    last_seen = Column(DateTime)
    phone_verification_code = Column(String(6))
    phone_verification_code_expiry_at = Column(DateTime())
    is_verified = Column(Boolean)
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)

    contacts = relationship(
        'User',
        secondary=contacts_association,
        primaryjoin=id == contacts_association.c.user_id,
        secondaryjoin=id == contacts_association.c.contact_id,
        backref=backref('contact_of', lazy='dynamic')
    )
    chatrooms = relationship(
        'ChatRoom',
        secondary=chatroom_members_association,
        back_populates='members'
    )
    chats = relationship('Chat',back_populates='sender')
    client_apps = relationship("ClientApp",back_populates="user")
    roles = relationship(
        'Role',
        secondary=user_roles_association,
        back_populates='users'
    )


    #initialize verification code and expiry time and save to the user
    async def initialize_verification_code(self,db:Session):
        code = generate_random_string(length=settings.verification_code_length)
        expiry_at = datetime.datetime.now() + datetime.timedelta(milliseconds=settings.verification_code_expiry_milliseconds)
        logger.info(f"User {self.phone} verification code initialized to {code} expires at {expiry_at}")
        self.phone_verification_code = code
        self.phone_verification_code_expiry_at = expiry_at
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    #validate the verification code
    async def validate_verification_code(self,code:str):
        logger.info(f"User {self.phone} verification code {code} vs {self.phone_verification_code} verification requested at {datetime.datetime.now()} vs {self.phone_verification_code_expiry_at}")
        if self.phone_verification_code == code and self.phone_verification_code_expiry_at > datetime.datetime.now():
            self.is_verified = True
            self.is_active = True
            self.phone_verification_code = None
            logger.info(f"User {self.phone} verified successfully")
            return True
        return False
    
    #create a jwt token for the user
    def create_jwt_token(self):
        logger.info(f"Creating JWT token for user {self.phone}")
        expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expiry_minutes)
        return jwt.encode({"sub":self.phone,"exp":expire},settings.jwt_secret_key,algorithm=settings.jwt_algorithm)


class ContentType(Model):
    __tablename__ = "content_types"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    content = Column(String(100))
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)
    permissions = relationship("Permission",back_populates="content_type")



class Permission(Model):
    __tablename__ = "permissions"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    name = Column(String(100))
    codename = Column(String(100))
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)
    content_type_id = Column(Uuid,ForeignKey("content_types.id"))
    content_type = relationship("ContentType",back_populates="permissions")
    roles = relationship(
        'Role',
        secondary=role_permissions_association,
        back_populates='permissions'
    )


class Role(Model):
    __tablename__ = "roles"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    name = Column(String(100))
    description = Column(String(500))
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)
    permissions = relationship(
        'Permission',
        secondary=role_permissions_association,
        back_populates='roles'
    )
    users = relationship(
        'User',
        secondary=user_roles_association,
        back_populates='roles'
    )


class ChatRoom(Model):
    __tablename__ = "chatrooms"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    fcm_room_id = Column(String(500),unique=True)
    socket_room_id = Column(String(500),unique=True)
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)

    members = relationship(
        'User',
        secondary=chatroom_members_association,
        back_populates='chatrooms'
    )
    group = relationship("Group", uselist=False, back_populates="chatroom")
    room_chats = relationship('Chat',back_populates='room')

    #ensure that the chatroom has at least two members
    def __init__(self,fcm_room_id:str,socket_room_id:str,members:List[User]):
        if not fcm_room_id:
            raise ValueError("FCM Room ID cannot be empty")
        if not socket_room_id:
            raise ValueError("Socket Room ID cannot be empty")
        if len(members) < 2:
            raise ValueError("Chatroom must have at least two members")
        
        self.fcm_room_id = fcm_room_id
        self.socket_room_id = socket_room_id
        self.members = members


class Group(Model):
    __tablename__ = "groups"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    name = Column(String(100))
    description = Column(String(500))
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)

    chatroom_id = Column(Uuid,ForeignKey("chatrooms.id"),unique=True,nullable=False)
    chatroom = relationship("ChatRoom",back_populates="group")


class Chat(Model):
    __tablename__ = "chats"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    message = Column(String(500),nullable=False)
    is_read = Column(Boolean,default=False)
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)

    sender_id = Column(Uuid,ForeignKey("users.id"),nullable=False)
    room_id = Column(Uuid,ForeignKey("chatrooms.id"),nullable=False)
    sender = relationship('User',back_populates='chats')
    room = relationship('ChatRoom',back_populates='room_chats')
    media = relationship("Media",back_populates="chat")

    #ensure that a user is a member of the chatroom before sending a message
    def __init__(self,message:str,sender:User,room:ChatRoom):
        if not message:
            raise ValueError("Message cannot be empty")
        if not sender:
            raise ValueError("Sender cannot be empty")
        if not room:
            raise ValueError("Room cannot be empty")
        if sender not in room.members:
            raise ValueError("Sender must be a member of the room")
        
        self.message = message
        self.sender = sender
        self.room = room


class Media(Model):
    __tablename__ = "media"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    link = Column(String(1024))
    type = Column(String(100))
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)

    chat_id = Column(Uuid,ForeignKey("chats.id"))
    chat = relationship('Chat',back_populates='media')


class ClientApp(Model):
    __tablename__ = "client_apps"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    name = Column(String(100))
    description = Column(String(500))
    client_id = Column(String(100),unique=True,default=generate_client_id)
    client_secret = Column(String(100),unique=True,default=generate_client_secret)
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)
    user_id = Column(Uuid,ForeignKey("users.id"))
    user = relationship("User",back_populates="client_apps")


    #set the client id and secret at creation
    def __init__(self,name:str,description:str,user:User):
        if not name:
            raise ValueError("App name cannot be empty")
        if not user:
            raise ValueError("User cannot be empty")
        if not description:
            raise ValueError("Description cannot be empty")
        
        self.name = name
        self.user = user
        self.description = description
        self.client_id = generate_client_id()
        self.client_secret = generate_client_secret()


