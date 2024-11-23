from fastapi.responses import JSONResponse

def response(code: int, message: str, type: str, data: any):
    response_data = {
        "code": code,
        "message": message,
        "data": data,
    }
    return (
        JSONResponse(status_code=code, content=response_data)
        if type == "error"
        else response_data
    )