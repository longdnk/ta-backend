import models.role.role as ModelRole
from database.database import engine

def initial_role():
    ModelRole.Base.metadata.create_all(bind=engine)