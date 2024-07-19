import datetime
from sqlalchemy.orm import Session
from pydantic import UUID4
import models as models
import schemas as schemas
from config import logger


# crud client app
async def create_client_app(db: Session, client_app_data: schemas.ClientAppCreate, user: models.User) -> models.ClientApp:
    logger.info(f"Creating client app with client name: {client_app_data.name} for user {user.phone}")
    client_app_db = models.ClientApp(**client_app_data.model_dump(),user=user)
    db.add(client_app_db)
    db.commit()
    db.refresh(client_app_db)
    return client_app_db

async def get_client_app(db: Session, id: UUID4) -> models.ClientApp:
    logger.info(f"Getting client app with id: {id}")
    return db.get_one(models.ClientApp,id)

async def get_client_apps(db: Session) -> list[models.ClientApp]:
    logger.info(f"Getting client apps")
    return db.query(models.ClientApp).all()

async def update_client_app(db: Session, id: UUID4, client_app_data: schemas.ClientAppUpdate) -> models.ClientApp:
    logger.info(f"Updating client app with id: {id}")
    client_app_db = await db.get_one(models.ClientApp,id)
    logger.info(f"Updating client app with id: {id}")
    client_app_db.update(client_app_data.model_dump())
    db.commit()
    db.refresh(client_app_db)
    return client_app_db

async def delete_client_app(db: Session, id: UUID4) -> models.ClientApp:
    logger.info(f"Deleting client app with id: {id}")
    client_app_db = await db.get_one(models.ClientApp,id)
    db.delete(client_app_db)
    db.commit()
    return client_app_db

    

# crud content type
async def create_content_type(db: Session, content_type_data: schemas.ContentTypeCreate) -> models.ContentType:
    logger.info(f"Creating content type with content: {content_type_data.content}")
    content_type_db = models.ContentType(**content_type_data.model_dump())
    db.add(content_type_db)
    db.commit()
    db.refresh(content_type_db)
    return content_type_db

async def get_content_type(db: Session, id: UUID4) -> models.ContentType:
    logger.info(f"Getting content type with id: {id}")
    return db.get_one(models.ContentType,id)

async def get_content_types(db: Session) -> list[models.ContentType]:
    logger.info(f"Getting content types")
    return db.query(models.ContentType).all()

async def update_content_type(db: Session, id: UUID4, content_type_data: schemas.ContentTypeUpdate) -> models.ContentType:
    logger.info(f"Updating content type with id: {id}")
    content_type_db = await db.get_one(models.ContentType,id)
    content_type_db.update(content_type_data.model_dump())
    db.commit()
    db.refresh(content_type_db)
    return content_type_db

async def delete_content_type(db: Session, id: UUID4) -> models.ContentType:
    logger.info(f"Deleting content type with id: {id}")
    content_type_db = await db.get_one(models.ContentType,id)
    db.delete(content_type_db)
    db.commit()
    return content_type_db

# crud permission