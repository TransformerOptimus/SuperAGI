from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log the details of the incoming request
    print(f"Received {request.method} request to {request.url}")
    response = await call_next(request)
    return response

@app.post("/webhook")
async def receive_webhook(request: Request):
    # Process the incoming webhook payload here
    # In this example, we'll just log the payload
    payload = await request.json()
    print("Received webhook payload:")
    print(payload)
    return {"message": "Webhook payload received successfully"}