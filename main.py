from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid, os, shutil

# ------------------------------
# FastAPI & CORS
# ------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Order Model
# ------------------------------
class Order(BaseModel):
    prompt: str
    model_type: str  # "new" or "recolor"
    user_email: str

orders = {}

# ------------------------------
# Root
# ------------------------------
@app.get("/")
def root():
    return {"message": "✅ Upland Kart API is running correctly!"}

# ------------------------------
# Create Order
# ------------------------------
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

# ------------------------------
# Check Status
# ------------------------------
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

# ------------------------------
# Complete Order → Generate Files
# ------------------------------
@app.post("/complete-order/{order_id}")
def complete_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")

    orders[order_id]["status"] = "ready"
    prompt = orders[order_id]["prompt"]

    # --------------------------
    # Generated files paths
    # --------------------------
    os.makedirs("generated", exist_ok=True)

    # Copy template files and rename them with order ID
    generated_files = {}
    templates = {
        "LOD0": "templates/lod_0_gltf.gltf",
        "LOD0_texture": "templates/lod_0_texture.jpg",
        "LOD1": "templates/lod_1_gltf.gltf",
        "LOD1_texture": "templates/lod_1_texture.jpg",
        "LOD2": "templates/lod_2_gltf.gltf",
        "LOD2_texture": "templates/lod_2_texture.jpg",
        "NFT_fullscreen": "templates/nft_fullscreen_gltf.gltf",
        "NFT_IPFS": "templates/nft_ipfs_gltf.gltf",
        "NFT_texture_carbody": "templates/nft_texture_carbody.jpg",
        "NFT_texture_wheel": "templates/nft_texture_wheel.jpg",
        "background": "templates/nft_ipfs.png"
    }

    for key, path in templates.items():
        filename = f"generated/{order_id}_{key}{os.path.splitext(path)[1]}"
        shutil.copyfile(path, filename)
        generated_files[key] = filename

    orders[order_id]["files"] = generated_files

    return {
        "order_id": order_id,
        "status": "ready",
        "files": orders[order_id]["files"]
    }
