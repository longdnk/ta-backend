import models.prompt.prompt as ModelPrompt
from database.database import engine

def initial_prompt():
    ModelPrompt.Base.metadata.create_all(bind=engine)