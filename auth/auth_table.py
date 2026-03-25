from auth_database import base, engine
import models

base.metadata.create_all(bind=engine) 