import time
from fastapi import Request
from mcp.server import FastMCP
import uvicorn
from fastapi import Response

mcp = FastMCP("iqnext-mcp")

@mcp.tool()
def add_num(num1: int, num2: int) -> int:
    """ 
    Add and return sum of two numbers
    """
    return num1 + num2

app = mcp.streamable_http_app()

@app.middleware('http')
async def middle(request: Request, call_next):
    
    start_time = time.perf_counter()
    print(f"Request : {request.headers}")
    auth = request.headers.get('Authorization')
    response = await call_next(request)
    print(f"Auth : {auth}")
    
    if auth is None:
        return Response(content="Invalid Request: Missing Authorization", status_code=401)
    else:
        if auth != "Bearer hello":
            return Response(content="Invalid Request: Invalid Authorization Token", status_code=401)
            
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)