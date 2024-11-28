from fastapi import (
    APIRouter,
    status,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Request,
    Depends,
)
from huggingface_hub import InferenceClient
from response.response_item import response
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
import asyncio
import time

client = InferenceClient(api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


# Pydantic model for login payload
class ChatInfo(BaseModel):
    model_name: str
    conservation: List[Dict[str, str]]
    max_token: int | None = None


model_router = APIRouter(prefix="/models", tags=["models"])

# Danh sách các model được phép
ALLOWED_MODELS = {
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
def run_model(chat_info: ChatInfo):
    try:
        # Kiểm tra model có được phép hay không
        if chat_info.model_name not in ALLOWED_MODELS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model '{chat_info.model_name}' is not allowed. Accepted models are: {', '.join(ALLOWED_MODELS)}",
            )

        # Trích xuất messages từ payload
        messages = chat_info.conservation

        # Gọi API inference
        completion = client.chat.completions.create(
            model=chat_info.model_name,  # Sử dụng model từ payload
            messages=messages,  # Nội dung hội thoại
            max_tokens=500 if chat_info.max_token is None else chat_info.max_token,  # Giới hạn số token
        )
        # Trả về phản hồi
        return {
            "code": status.HTTP_200_OK,
            "message": "Generated success",
            "data": completion.choices[0].message.content,
        }

    except HTTPException as e:
        raise e  # Ném lại lỗi HTTPException để FastAPI xử lý

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@model_router.websocket("/inference")
async def streaming_chat(websocket: WebSocket):
    await websocket.accept()
    response = Response(websocket=websocket)
    try:
        while True:
            try:
                # Lắng nghe dữ liệu từ client
                payload = await websocket.receive_json()
                # Xử lý payload tại đây...
            except WebSocketDisconnect:
                break  # Thoát khỏi vòng lặp nếu WebSocket bị ngắt kết nốiA

            # Parse payload
            model_name, messages, max_token, stream_mode = parse_payload(payload=payload)
            # Kiểm tra model hợp lệ
            if model_name not in ALLOWED_MODELS:
                await websocket.send_json({"error": "Model not allowed."})
                await websocket.close()
                return

            # Gọi Hugging Face với chế độ stream
            stream = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=500 if max_token is None else max_token,
                stream=True,
            )

            if stream_mode == 'token' or stream_mode is None:
                await response.stream_token(stream=stream)
            elif stream_mode == 'digit':
                await response.stream_digit(stream=stream)
            elif stream_mode == 'word':
                await response.stream_word(stream=stream)

            await websocket.send_json({"status": "done"})

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        await websocket.close()

    except Exception as e:
        # Gửi lỗi nếu có bất kỳ ngoại lệ nào
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
        self.websocket = websocket  # Lưu websocket để gửi dữ liệu

    async def stream_token(self, stream):
        # Gửi từng chunk qua WebSocket
        for chunk in stream:
            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
            await self.websocket.send_json({"text": content})
            await asyncio.sleep(0.02)

    async def stream_digit(self, stream):
        buffer = ""  # Bộ đệm để lưu trữ nội dung trước khi gửi
        for chunk in stream:
            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
            if content:
                buffer += content  # Thêm nội dung mới vào buffer

                # Khi buffer có đủ 10 ký tự, gửi đi và cắt phần đã gửi
                while len(buffer) >= 10:
                    await self.websocket.send_json({"content": buffer[:10]})
                    buffer = buffer[10:]
                    await asyncio.sleep(0.02)  # Thêm độ trễ 0.05 giây

    async def stream_word(self, stream):
        buffer = []  # Lưu trữ các từ
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                buffer.extend(content.split())  # Chia nhỏ chunk thành các từ và thêm vào buffer

                # Gửi mỗi lần 5 từ
                while len(buffer) >= 5:
                    await self.websocket.send_json({"content": " ".join(buffer[:5])})
                    buffer = buffer[5:]  # Xóa 10 từ đã gửi
                    await asyncio.sleep(0.02)
