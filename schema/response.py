from typing import Any
from pydantic import BaseModel
from fastapi.responses import JSONResponse

class ResponseMessage(BaseModel):
    code: int
    message: str
    data: Any = None
    error: bool = False

    def process_data(self, data):
        if isinstance(data, list):
            return [item.to_dict() if hasattr(item, "to_dict") else item for item in data]
        elif hasattr(data, "to_dict"):
            return data.to_dict()
        return data

    def to_response(self) -> JSONResponse:
        processed_data = self.process_data(self.data)
        response_data = {
            "code": self.code,
            "message": self.message,
            "data": processed_data,
        }
        return JSONResponse(status_code=self.code, content=response_data)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.to_response()