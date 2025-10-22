from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import time

app = FastAPI(title="Upland Kart Generator API")

# ✅ Allow Base44 live, preview, and localhost (for testing)
origins = [
    "https://upland-kart-studio-b82351ca.base44.app",
    "https://preview--upland-kart-studio-b82351ca.base44.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧾 Simple in-memory storage (for testing)
ORDERS = {}

# Input structure for requests
class OrderRequest(BaseModel):
    prompt: str
    model_type: str  # "new" or "recolor"
    user_email: str

# 🔧 Endpoint to create a new GoKart order
@app.post("/create-order")
async def create_order(req: OrderRequest):
    order_id = str(uuid.uuid4())
    price = 120 if req.model_type == "new" else 30

    ORDERS[order_id] = {
        "prompt": req.prompt,
        "model_type": req.model_type,
        "user_email": req.user_email,
        "status": "processing",
        "price": price,
        "created_at": time.time(),
    }

    # Simulate generation delay (this would be your AI generation backend)
    time.sleep(2)
    ORDERS[order_id]["status"] = "ready"
    ORDERS[order_id]["files"] = {
        "LOD0": f"https://ipfs.io/ipfs/{order_id}_LOD0.glb",
        "LOD1": f"https://ipfs.io/ipfs/{order_id}_LOD1.glb",
        "LOD2": f"https://ipfs.io/ipfs/{order_id}_LOD2.glb",
        "NFT": f"https://ipfs.io/ipfs/{order_id}_NFT.png",
        "BACKGROUND": f"https://ipfs.io/ipfs/{order_id}_BACKGROUND.png",
    }

    return {
        "order_id": order_id,
        "price": price,
        "status": ORDERS[order_id]["status"],
        "message": "Order successfully created. Awaiting payment."
    }

# 🔍 Endpoint to check order status
@app.get("/status/{order_id}")
async def get_status(order_id: str):
    if order_id not in ORDERS:
        return {"error": "Order not found."}
    return ORDERS[order_id]

# 🧩 Endpoint to simulate AI model generation completion
@app.post("/complete/{order_id}")
async def complete_order(order_id: str):
    if order_id not in ORDERS:
        return {"error": "Order not found."}
    ORDERS[order_id]["status"] = "ready"
    return {"message": f"Order {order_id} marked as ready."}

# 🏁 Root endpoint for quick API test
@app.get("/")
async def root():
    return {"message": "✅ Upland Kart Generator Backend is running successfully!"}
