import uvicorn
from dotenv import load_dotenv
from param_compile import params
load_dotenv()
from routes.auth import auth_router
from routes.role import role_router
from routes.chat import chat_router
from routes.user import user_router
from routes.model import model_router
from routes.prompt import prompt_router
from schema.response import ResponseMessage
from fastapi import FastAPI, status, Request
from routes.permission import permission_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_item = exc.errors()[0]
    return ResponseMessage(
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Invalid request entity",
        data={
            "error": f"{error_item['msg']}",
            "error_field": f"{error_item['input']}",
            "detail": f"{error_item}",
        },
    )


routers = [
    auth_router,
    user_router,
    chat_router,
    role_router,
    permission_router,
    prompt_router,
    model_router,
]

for router in routers:
    app.include_router(router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"code": status.HTTP_200_OK, "message": "Check health Done"}


def run_server():
    return uvicorn.run(
        "backend:app",
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