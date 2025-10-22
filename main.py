from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

app = FastAPI()

# ✅ CORS configuration (critical: must be before any routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class Order(BaseModel):
    prompt: str
    model_type: str
    user_email: str

orders = {}

@app.get("/")
def root():
    return {"message": "✅ Upland Kart API is running correctly!"}

@app.post("/create-order")
def create_order(order: Order):
    order_id = str(uuid.uuid4())
    orders[order_id] = {
        "prompt": order.prompt,
        "model_type": order.model_type,
        "user_email": order.user_email,
        "status": "pending",
        "price": 120 if order.model_type == "new" else 30
    }
    return {"order_id": order_id, "price": orders[order_id]["price"]}

@app.get("/status/{order_id}")
def get_status(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order_id": order_id, "status": orders[order_id]["status"]}

@app.post("/complete-order/{order_id}")
def complete_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    orders[order_id]["status"] = "ready"
    orders[order_id]["files"] = {
        "LOD0": "https://example.com/lod0.glb",
        "LOD1": "https://example.com/lod1.glb",
        "LOD2": "https://example.com/lod2.glb",
        "texture": "https://example.com/texture.jpg"
    }
    return {"order_id": order_id, "status": "ready", "files": orders[order_id]["files"]}
