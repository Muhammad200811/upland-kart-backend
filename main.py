from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

app = FastAPI()

# ⚠️ MUST ADD THIS BEFORE ANY ROUTES
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for testing; can restrict later
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, etc.
    allow_headers=["*"],   # Any headers
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
    price = 120 if order.model_type == "new" else 30
    orders[order_id] = {
        "prompt": order.prompt,
        "model_type": order.model_type,
        "user_email": order.user_email,
        "status": "pending",
        "price": price
    }
    return {"order_id": order_id, "price": price}

@app.get("/status/{order_id}")
def get_status(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    order = orders[order_id]
    return {
        "order_id": order_id,
        "status": order["status"],
        "files": order.get("files")
    }

@app.post("/complete-order/{order_id}")
def complete_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    orders[order_id]["status"] = "ready"
    orders[order_id]["files"] = {
        "LOD0": "https://storage.googleapis.com/upland-kart-files/placeholder_assets/LOD0.glb",
        "LOD1": "https://storage.googleapis.com/upland-kart-files/placeholder_assets/LOD1.glb",
        "LOD2": "https://storage.googleapis.com/upland-kart-files/placeholder_assets/LOD2.glb",
        "NFT_fullscreen": "https://storage.googleapis.com/upland-kart-files/placeholder_assets/NFT_fullscreen.jpg",
        "NFT_IPFS": "https://storage.googleapis.com/upland-kart-files/placeholder_assets/NFT_IPFS.jpg",
        "background": "https://storage.googleapis.com/upland-kart-files/placeholder_assets/Background.png"
    }
    
    return {
        "order_id": order_id,
        "status": "ready",
        "files": orders[order_id]["files"]
    }
