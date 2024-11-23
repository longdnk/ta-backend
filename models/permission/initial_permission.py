import models.permission.permission as ModelPermission
from database.database import engine

def initial_permission():
    ModelPermission.Base.metadata.create_all(bind=engine)