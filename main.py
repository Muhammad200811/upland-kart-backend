from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI()

# --- CORS so Base44 can access your API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OrderRequest(BaseModel):
    prompt: str
    model_type: str  # "new" or "recolor"
    user_email: str

orders = {}

@app.get("/")
def home():
    return {"status": "Upland Kart API is running"}

@app.post("/create-order")
def create_order(req: OrderRequest):
    order_id = f"ORD-{int(time.time())}"
    orders[order_id] = {
        "prompt": req.prompt,
        "type": req.model_type,
        "email": req.user_email,
        "status": "processing",
    }
    print(f"[INFO] Generating model for {req.prompt} ({req.model_type})")

    time.sleep(2)
    orders[order_id]["status"] = "ready"
    orders[order_id]["download_url"] = f"https://upland-kart-api.onrender.com/download/{order_id}"
    return {"order_id": order_id, "price": 120 if req.model_type == "new" else 30}

@app.get("/status/{order_id}")
def get_status(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]

@app.get("/download/{order_id}")
def download(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    if orders[order_id]["status"] != "ready":
        raise HTTPException(status_code=400, detail="Model not ready yet")
    return {
        "message": "Here’s your GoKart model files (mock link)",
        "LOD0": "https://example.com/gokart_LOD0.gltf",
        "LOD1": "https://example.com/gokart_LOD1.gltf",
        "LOD2": "https://example.com/gokart_LOD2.gltf",
        "NFT": "https://example.com/gokart_NFT.jpg",
        "BACKGROUND": "https://example.com/gokart_background.png"
    }