from auth_database import base, engine
import model

base.metadata.create_all(bind=engine)