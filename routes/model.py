import os
import json
import time
import asyncio
from fastapi import (
    APIRouter,
    status,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Request,
    Depends,
    Response
)
from fastapi.responses import StreamingResponse
from huggingface_hub import InferenceClient
from response.response_item import response
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
from param_compile import params

key = os.environ.get("HF_TOKEN")
client = InferenceClient(api_key=key)
DELAY_THRESHOLD = params.web_socket_time

# Pydantic model for login payload
class ChatInfo(BaseModel):
    model_name: str
    conservation: List[Dict[str, str]]
    max_token: int | None = None


model_router = APIRouter(prefix="/models", tags=["models"])

# Danh sách các model được phép
ALLOWED_MODELS = {
    "Qwen/QwQ-32B-Preview",
    "Qwen/Qwen2.5-72B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "meta-llama/Llama-3.2-1B-Instruct",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
    "microsoft/Phi-3.5-mini-instruct",
    "microsoft/Phi-3-mini-4k-instruct",
}

@model_router.post("/inference", status_code=status.HTTP_200_OK)
async def run_model(chat_info: ChatInfo):
    messages = chat_info.conservation
    model = chat_info.model_name
    max_token = chat_info.max_token if chat_info.max_token is not None else 500

    await asyncio.sleep(1)

    async def generate_stream():
        try:
            # Create a stream from Hugging Face API
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_token,
                stream=True,
            )
            # Iterate through the stream and yield text content
            for chunk in stream:
                content = chunk.choices[0].delta.content
                yield content
                await asyncio.sleep(DELAY_THRESHOLD)  # Yield control to event loop

        except Exception as e:
            yield f"Error: {str(e)}\n"

    return StreamingResponse(generate_stream(), media_type="text/plain")

@model_router.websocket("/inference")
async def streaming_chat(websocket: WebSocket):
    await websocket.accept()
    response = Response(websocket=websocket)
    is_cancelled = False
    try:
        while True:
            try:
                payload = await websocket.receive_json()

                if payload.get("action") == "cancel":
                    is_cancelled = True
                    await websocket.send_json({"status": "cancelled"})
                    break

                if is_cancelled:
                    break

                model_name, messages, max_token, stream_mode = parse_payload(payload=payload)

                if model_name not in ALLOWED_MODELS:
                    await websocket.send_json({"error": "Model not allowed."})
                    await websocket.close()
                    return

                stream = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=500 if max_token is None else max_token,
                    temperature=params.model_temp,
                    stream=True,
                )

                if stream_mode == 'token' or stream_mode is None:
                    await response.stream_token(stream=stream)
                elif stream_mode == 'digit':
                    await response.stream_digit(stream=stream)
                elif stream_mode == 'word':
                    await response.stream_word(stream=stream)

                await websocket.send_json({"text": None, "status": "done"})

            except WebSocketDisconnect:
                break  

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        await websocket.close()

    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()

def parse_payload(payload):
    model_name = payload.get("model_name")
    messages = payload.get("conservation")
    max_token = payload.get("max_token")
    stream_mode = payload.get("stream_mode")
    return model_name, messages, max_token, stream_mode

class Response():    
    def __init__(self, websocket):
        self.websocket = websocket

    async def stream_token(self, stream, is_cancelled = False):
        for chunk in stream:
            if is_cancelled:
                break
            content = chunk.choices[0].delta.content
            await self.websocket.send_json({"text": content, "status": "continue"})
            await asyncio.sleep(DELAY_THRESHOLD)

    async def stream_digit(self, stream, is_cancelled = False):
        buffer = ""  
        for chunk in stream:
            if is_cancelled:
                break
            content = chunk.choices[0].delta.content
            if content:
                buffer += content  

                while len(buffer) >= 5:
                    await self.websocket.send_json({"text": buffer[:5], "status": "continue"})
                    buffer = buffer[5:]
                    await asyncio.sleep(DELAY_THRESHOLD)
        if buffer:
            await self.websocket.send_json({ "text": buffer, "status": "continue" })

    async def stream_word(self, stream, is_cancelled = False):
        buffer = []  
        for chunk in stream:
            if is_cancelled:
                break
            content = chunk.choices[0].delta.content
            if content:
                buffer.extend(content.split())  
                while len(buffer) >= 5:
                    await self.websocket.send_json({"text": " ".join(buffer[:5]), "status": "continue"})
                    buffer = buffer[5:]  
                    await asyncio.sleep(DELAY_THRESHOLD)
        if buffer:
            await self.websocket.send_json({ "text": " ".join(buffer), "status": "continue" })
