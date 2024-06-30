from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from models import *
from config import settings,TEST_DATABASE_URL


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
    media = Media(link="test_link",type="test_type",chat=chat)
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