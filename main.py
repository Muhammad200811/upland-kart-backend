from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import json

app = FastAPI()

# ✅ CORS Setup for your Base44 frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://upland-kart-studio-b82351ca.base44.app",
        "https://preview--upland-kart-studio-b82351ca.base44.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Request & Order Models
# ------------------------------
class OrderRequest(BaseModel):
    prompt: str
    model_type: str  # "new" or "recolor"
    user_email: str

class OrderStatus(BaseModel):
    order_id: str
    status: str
    download_link: Optional[str] = None

# In-memory order store (for demo purposes)
orders = {}

# ------------------------------
# Create Order Endpoint
# ------------------------------
@app.post("/create-order")
async def create_order(order: OrderRequest):
    if not order.prompt or not order.model_type or not order.user_email:
        raise HTTPException(status_code=400, detail="Missing required fields")

    order_id = str(uuid.uuid4())
    
    # Example pricing logic
    price = 120 if order.model_type == "new" else 30

    # Save order to memory
    orders[order_id] = {
        "prompt": order.prompt,
        "model_type": order.model_type,
        "user_email": order.user_email,
        "price": price,
        "status": "pending",
        "download_link": None
    }

    # Here you would trigger your GoKart generation workflow
    # (e.g., Blender automation, AI model, LOD exports, IPFS upload, etc.)

    return {
        "order_id": order_id,
        "price": price,
        "status": "pending"
    }

# ------------------------------
# Check Order Status Endpoint
# ------------------------------
@app.get("/status/{order_id}")
async def get_status(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders[order_id]

    # Example: mark ready automatically for testing
    if order["status"] == "pending":
        order["status"] = "ready"
        order["download_link"] = f"https://example.com/downloads/{order_id}.zip"

    return {
        "order_id": order_id,
        "status": order["status"],
        "download_link": order["download_link"]
    }

# ------------------------------
# Health Check
# ------------------------------
@app.get("/")
async def root():
    return {"message": "Upland GoKart backend is running"}
