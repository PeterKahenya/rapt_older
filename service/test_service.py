from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from models import *
from config import settings,TEST_DATABASE_URL
from schemas import *


@pytest.fixture(scope="session")
def db():
    engine = create_engine(TEST_DATABASE_URL)
    connection = engine.connect()
    connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.test_database_name};"))
    connection.close()

    engine = create_engine(f"{TEST_DATABASE_URL}/{settings.test_database_name}")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Model.metadata.create_all(engine)
    session = SessionLocal(bind=engine)
    yield session
    session.rollback()
    session.close()
    Model.metadata.drop_all(bind=engine)
    engine.dispose()


"""Test Models"""

#test user creation
def test_user_creation(db):
    user = User(name="Test User", phone="1234567890")
    db.add(user)
    db.commit()
    assert user in db


#test add user to contacts
def test_add_user_to_contacts(db):
    user1 = User(name="Test User 1", phone="1234567891")
    user2 = User(name="Test User 2", phone="1234567892")
    user1.contacts.append(user2)
    db.add(user1)
    db.commit()
    assert user2 in user1.contacts


#test chatroom creation
def test_chatroom_creation(db):
    user1 = User(name="Test User 1", phone="1234567899")
    user2 = User(name="Test User 1", phone="1234567898")
    chatroom = ChatRoom(fcm_room_id="test_fcm_room_id",socket_room_id="test_socket_room_id",members=[user1,user2])
    db.add(chatroom)
    db.commit()
    assert chatroom in db


#test add user to chatroom
def test_add_user_to_chatroom(db):
    user = User(name="Test User", phone="1234567893")
    user1 = User(name="Test User 1", phone="1234567896")
    user2 = User(name="Test User 1", phone="1234567897")
    chatroom = ChatRoom(fcm_room_id="test_fcm_room_id1",socket_room_id="test_socket_room_id1",members=[user1,user2])
    chatroom.members.append(user)
    db.add(chatroom)
    db.commit()
    assert user in chatroom.members


#test group creation
def test_group_creation(db):
    user1 = User(name="Test User 1", phone="1334567896")
    user2 = User(name="Test User 1", phone="1334567897")
    chat = ChatRoom(fcm_room_id="test_fcm_room_id2",socket_room_id="test_socket_room_id2",members=[user1,user2])
    group = Group(name="Test Group",description="Test Group Description",chatroom=chat)
    db.add(group)
    db.commit()
    assert group in db


#test add user to group
def test_add_user_to_group(db):
    user = User(name="Test User", phone="1234567894")
    user1 = User(name="Test User 1", phone="1434567896")
    user2 = User(name="Test User 1", phone="1434567897")
    chatroom = ChatRoom(fcm_room_id="test_fcm_room_id3",socket_room_id="test_socket_room_id3",members=[user1,user2])
    group = Group(name="Test Group",description="Test Group Description",chatroom=chatroom)
    group.chatroom.members.append(user)
    db.add(group)
    db.commit()
    assert user in group.chatroom.members


#test chat creation
def test_chat_creation(db):
    user1 = User(name="Test User 1", phone="1534567896")
    user2 = User(name="Test User 1", phone="1534567897")
    chatroom = ChatRoom(fcm_room_id="test_fcm_room_id4",socket_room_id="test_socket_room_id4",members=[user1,user2])
    chat = Chat(message="Test Message",sender=user1,room=chatroom)
    db.add(chat)
    db.commit()
    assert chat in db


#test add media to chat
def test_add_media_to_chat(db):
    user1 = User(name="Test User 1", phone="1634567896")
    user2 = User(name="Test User 1", phone="1634567897")
    chatroom = ChatRoom(fcm_room_id="test_fcm_room_id5",socket_room_id="test_socket_room_id5",members=[user1,user2])
    chat = Chat(message="Test Message",sender=user1,room=chatroom)
    media = Media(link="test_link",file_type="test_type",chat=chat)
    db.add(media)
    db.commit()
    assert media in db


#test app creation by providing app name and user
def test_app_creation(db):
    user = User(name="Test User", phone="1234567777")
    capp = ClientApp(name="Test App",user=user,description="Test App Description")
    db.add(capp)
    db.commit()
    assert capp in db
    assert capp.client_id is not None and capp.client_secret is not None


#test content_type creation 
def test_content_type_creation(db):
    content_type = ContentType(content = "users")
    db.add(content_type)
    db.commit()
    assert content_type in db

# test permission creation
def test_permission_creation(db):
    content_type = ContentType(content = "users")
    permission = Permission(name="Can View Users",codename="view_users",content_type=content_type)
    db.add(permission)
    db.commit()
    assert permission in db


#test role creation
def test_role_creation(db):
    content_type = ContentType(content = "users")
    permission1 = Permission(name="Can View Users",codename="view_users",content_type=content_type)
    permission2 = Permission(name="Can Edit Users",codename="edit_users",content_type=content_type)
    role = Role(name="Admin",description="Admin Role")
    role.permissions.append(permission1)
    role.permissions.append(permission2)
    db.add(role)
    db.commit()
    assert role in db


#test user role assignment
def test_user_role_assignment(db):
    user = User(name="Test User", phone="1234567895")
    content_type = ContentType(content = "users")
    permission1 = Permission(name="Can View Users",codename="view_users",content_type=content_type)
    permission2 = Permission(name="Can Edit Users",codename="edit_users",content_type=content_type)
    role = Role(name="Admin",description="Admin Role")
    role.permissions.append(permission1)
    role.permissions.append(permission2)
    user.roles.append(role)
    db.add(user)
    db.commit()
    assert role in user.roles




 
"""Test Schemas"""

#test clientapp schemas
def test_clientapp_schema(db):
    #test create clientapp object
    client_app = ClientAppCreate(**{"name": "Test App","description": "Test App Description"})
    assert client_app.name == "Test App"
    
    #test update clientapp object
    client_app_update = ClientAppUpdate(**{"name": "Test App1","description": "Test App Description1"})
    assert client_app_update.name == "Test App1"

    #test get clientapp object
    client_app_get = db.query(ClientApp).first()
    client_app_schema = ClientAppInDBBase.model_validate(client_app_get)
    assert client_app_schema.name == client_app_get.name
    assert client_app_schema.description == client_app_get.description


#test contenttype schemas
def test_contenttype_schema(db):
    #test create contenttype object
    content_type = ContentTypeCreate(**{"content": "users"})
    assert content_type.content == "users"
    
    #test update contenttype object
    content_type_update = ContentTypeUpdate(**{"content": "users1"})
    assert content_type_update.content == "users1"

    #test get contenttype object
    content_type_get = db.query(ContentType).first()
    content_type_schema = ContentTypeInDBBase.model_validate(content_type_get)
    assert content_type_schema.content == content_type_get.content


#test permission schemas
def test_permission_schema(db):
    #test create permission object
    content_type = db.query(ContentType).first()
    permission = PermissionCreate(**{"name": "Can View Users","codename": "view_users","content_type_id": content_type.id})
    assert permission.name == "Can View Users"
    assert permission.codename == "view_users"
    
    #test update permission object
    permission_update = PermissionUpdate(**{"name": "Can View Users1","codename": "view_users1","content_type_id": content_type.id})
    assert permission_update.name == "Can View Users1"
    assert permission_update.codename == "view_users1"

    #test get permission object
    permission_get = db.query(Permission).first()
    permission_schema = PermissionInDBBase.model_validate(permission_get)
    assert permission_schema.name == permission_get.name
    assert permission_schema.codename == permission_get.codename
    assert permission_schema.content_type.content == permission_get.content_type.content


#test role schemas
def test_role_schema(db):
    #test create role object
    role_create = RoleCreate(**{"name": "Admin","description": "Admin Role"})
    assert role_create.name == "Admin"
    assert role_create.description == "Admin Role"
    
    #test update role object
    permission1 = db.query(Permission).first()
    permission2 = db.query(Permission).all()[1]
    role_update = RoleUpdate(**{
        "name": "Admin1",
        "description": "Admin Role1",
        "permissions": [permission1.to_dict(),permission2.to_dict()]
        })
    assert role_update.name == "Admin1"
    assert role_update.description == "Admin Role1"

    #test get role object
    role_get = db.query(Role).first()
    role_schema = RoleInDBBase.model_validate(role_get)
    print(role_schema)
    assert role_schema.name == role_get.name
    assert role_schema.description == role_get.description
    assert role_schema.permissions[0].name == role_get.permissions[0].name
    assert role_schema.permissions[1].name == role_get.permissions[1].name


#test user schemas
def test_user_schema(db):
    #test create user object
    user_create = UserCreate(**{"name": "Test User","phone": "1234567890"})
    assert user_create.name == "Test User"
    assert user_create.phone == "1234567890"
    
    #test update user object
    user_update = UserUpdate(**{"name": "Test User1","phone": "1234567891","roles": [],"contacts": []})
    assert user_update.name == "Test User1"
    assert user_update.phone == "1234567891"

    #test get user object
    user_get = db.query(User).first()
    user_schema = UserInDBBase.model_validate(user_get)
    assert user_schema.name == user_get.name
    assert user_schema.phone == user_get.phone


#test chatroom schemas
def test_chatroom_schema(db):
    #test create chatroom object
    user1 = db.query(User).first()
    user2 = db.query(User).all()[1]
    chatroom_create = ChatRoomCreate(**{"fcm_room_id": "test_fcm_room_id","socket_room_id": "test_socket_room_id","members": [user1.to_dict(),user2.to_dict()]})
    assert chatroom_create.fcm_room_id == "test_fcm_room_id"
    assert chatroom_create.socket_room_id == "test_socket_room_id"
    
    #test update chatroom object
    user = db.query(User).all()[2]
    chatroom_update = ChatRoomUpdate(**{"fcm_room_id": "test_fcm_room_id1","socket_room_id": "test_socket_room_id1","members": [user.to_dict()]})
    assert chatroom_update.fcm_room_id == "test_fcm_room_id1"
    assert chatroom_update.socket_room_id == "test_socket_room_id1"

    #test get chatroom object
    chatroom_get = db.query(ChatRoom).first()
    chatroom_schema = ChatRoomInDBBase.model_validate(chatroom_get)
    assert chatroom_schema.fcm_room_id == chatroom_get.fcm_room_id
    assert chatroom_schema.socket_room_id == chatroom_get.socket_room_id

#test group schemas
def test_group_schema(db):
    #test create group object
    chatroom = db.query(ChatRoom).first()
    group_create = GroupCreate(**{"name": "Test Group","description": "Test Group Description","chatroom": chatroom.to_dict()})
    assert group_create.name == "Test Group"
    assert group_create.description == "Test Group Description"
    
    #test update group object
    user = db.query(User).all()[2]
    group_update = GroupUpdate(**{"name": "Test Group1","description": "Test Group Description1","chatroom_id": chatroom.id})
    assert group_update.name == "Test Group1"
    assert group_update.description == "Test Group Description1"

    #test get group object
    group_get = db.query(Group).first()
    group_schema = GroupInDBBase.model_validate(group_get)
    assert group_schema.name == group_get.name
    assert group_schema.description == group_get.description


#test chat schemas
def test_chat_schema(db):
    #test create chat object
    user1 = db.query(User).first()
    chatroom = db.query(ChatRoom).first()
    chat_create = ChatCreate(**{"message": "Test Message","sender": user1.to_dict(),"room": chatroom.to_dict()})
    assert chat_create.message == "Test Message"
    
    #test update chat object
    media = db.query(Media).first()
    chat_update = ChatUpdate(**{"message": "Test Message1","is_read": True,"media": [media.to_dict()]})
    assert chat_update.message == "Test Message1"

    #test get chat object
    chat_get = db.query(Chat).first()
    chat_schema = ChatInDBBase.model_validate(chat_get)
    assert chat_schema.message == chat_get.message


#test media schemas
def test_media_schema(db):
    #test create media object
    media_create = MediaCreate(**{"link": "https://test_link","file_type": "mp4"})
    assert media_create.link == "https://test_link"
    assert media_create.file_type == "mp4"
    
    #test update media object
    media_update = MediaUpdate(**{"link": "test_link1","file_type": "test_type1"})
    assert media_update.link == "test_link1"
    assert media_update.file_type == "test_type1"

    #test get media object
    media_get = db.query(Media).first()
    media_schema = MediaInDBBase.model_validate(media_get)
    assert media_schema.link == media_get.link
    assert media_schema.file_type == media_get.file_type


