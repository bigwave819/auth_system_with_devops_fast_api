from .auth_database import base, engine
from . import models

base.metadata.create_all(bind=engine) 