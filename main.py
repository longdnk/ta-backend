from models.permission.initial_permission import initial_permission
from models.prompt.initial_prompt import initial_prompt
from fastapi.middleware.cors import CORSMiddleware
from models.user.initial_user import initial_user
from models.chat.initial_chat import initial_chat
from models.role.initial_role import initial_role
from routes.permission import permission_router
from routes.prompt import prompt_router
from routes.model import model_router
from routes.auth import auth_router
from routes.role import role_router
from routes.user import user_router
from routes.chat import chat_router
from routes.rag import rag_router
from fastapi import FastAPI, status
from param_compile import params
import uvicorn

app = FastAPI()

# Initial Model
initial_permission()
initial_prompt()
initial_role()
initial_user()

# App Routes
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(permission_router)
app.include_router(chat_router)
app.include_router(prompt_router)
app.include_router(model_router)
app.include_router(rag_router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "*"
    ], 
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"code": status.HTTP_200_OK, "message": "Check Health in root path OK"}


def run_server():
    return uvicorn.run(
        "main:app",
        host=params.host,
        port=params.port,
        reload=params.reload,
        workers=params.workers,
        backlog=params.backlog,
        log_level=params.log_level,
        use_colors=params.use_colors,
        limit_concurrency=params.limit_concurrency,
        limit_max_requests=params.limit_max_requests,
        ssl_keyfile=params.ssl_keyfile,
        ssl_certfile=params.ssl_certfile,
    )


if __name__ == "__main__":
    run_server()