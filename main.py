from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os
import shutil

app = FastAPI()

# ⚠️ CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your Base44 domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Order model
# -----------------------------
class Order(BaseModel):
    prompt: str
    model_type: str  # "new" or "recolor"
    user_email: str

# -----------------------------
# In-memory orders store
# -----------------------------
orders = {}

# -----------------------------
# Helper function to "generate" background
# -----------------------------
def generate_background(prompt: str):
    src = os.path.join(os.path.dirname(__file__), "nft_ipfs.png")
    dst = os.path.join("/tmp", f"{prompt}_background.png")
    shutil.copyfile(src, dst)
    return dst

# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "✅ Upland Kart API is running correctly!"}

# -----------------------------
# Create order
# -----------------------------
@app.post("/create-order")
def create_order(order: Order):
    order_id = str(uuid.uuid4())

    # Assign price
    price = 120 if order.model_type == "new" else 30

    # Generate background (copies example image)
    background_file = generate_background(order.prompt)

    # Assign files (use your uploaded files)
    files = {
        "LOD0": "lod_0_gltf.gltf",
        "LOD0_texture": "lod_0_texture.jpg",
        "LOD1": "lod_1_gltf.gltf",
        "LOD1_texture": "lod_1_texture.jpg",
        "LOD2": "lod_2_gltf.gltf",
        "LOD2_texture": "lod_2_texture.jpg",
        "NFT_fullscreen": "nft_fullscreen_gltf.gltf",
        "NFT_IPFS": "nft_ipfs_gltf.gltf",
        "NFT_texture_carbody": "nft_texture_carbody.jpg",
        "NFT_texture_wheel": "nft_texture_wheel.jpg",
        "background": background_file
    }

    # Save order
    orders[order_id] = {
        "prompt": order.prompt,
        "model_type": order.model_type,
        "user_email": order.user_email,
        "status": "pending",
        "price": price,
        "files": files
    }

    return {"order_id": order_id, "price": price, "files": files}

# -----------------------------
# Check order status
# -----------------------------
@app.get("/status/{order_id}")
def get_status(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order_id": order_id,
        "status": orders[order_id]["status"],
        "files": orders[order_id]["files"]
    }

# -----------------------------
# Complete order (simulate generation ready)
# -----------------------------
@app.post("/complete-order/{order_id}")
def complete_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    orders[order_id]["status"] = "ready"
    return {
        "order_id": order_id,
        "status": "ready",
        "files": orders[order_id]["files"]
    }

