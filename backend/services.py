import datetime as _dt

import fastapi as _fastapi
import fastapi.security as _security
import jwt as _jwt
import passlib.hash as _hash
import sqlalchemy.orm as _orm

import database as _database
import models as _models
import schemas as _schemas

JWT_SECRET = "myjwtsecret"

oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()


async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    user_obj = _models.User(
        email=user.email, hashed_password=_hash.bcrypt.hash(user.password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(email, db)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


async def create_token(
    user: _models.User,
):
    user_obj = _schemas.User.from_orm(user)

    token = _jwt.encode(user_obj.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(
    db: _orm.Session = _fastapi.Depends(get_db),
    token: str = _fastapi.Depends(oauth2schema),
) -> _schemas.User:
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return _schemas.User.from_orm(user)


async def create_lead(user: _schemas.User, db: _orm.Session, lead: _schemas.LeadCreate):
    lead_obj = _models.Lead(**lead.dict(), owner_id=user.id)
    db.add(lead_obj)
    db.commit()
    db.refresh(lead_obj)
    return lead_obj


async def get_leads(
    user: _schemas.User,
    db: _orm.Session,
):
    return db.query(_models.Lead).filter(_models.Lead.owner_id == user.id).all()


async def get_lead(
    user: _schemas.User,
    db: _orm.Session,
    lead_id: int,
) -> _models.Lead:
    lead = (
        db.query(_models.Lead)
        .filter(_models.Lead.owner_id == user.id, _models.Lead.id == lead_id)
        .first()
    )
    if not lead:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )
    return lead


async def delete_lead(
    user: _schemas.User,
    db: _orm.Session,
    lead_id: int,
):
    lead = await get_lead(user, db, lead_id)
    db.delete(lead)
    db.commit()
    return {'message': 'Lead deleted'}

async def update_lead(
    user: _schemas.User,
    db: _orm.Session,
    lead_id: int,
    lead: _schemas.LeadCreate,
):
    lead_obj = await get_lead(user, db, lead_id)
    for key, value in lead.dict().items():
        setattr(lead_obj, key, value)
    lead_obj.date_last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(lead_obj)
    
    return lead_obj


