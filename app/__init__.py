from .database import Base, engine
from . import models, schemas, crud, auth

# Create tables
models.Base.metadata.create_all(bind=engine)