from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import shutil
import os

app = FastAPI()

# ⚠️ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to your Base44 domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Order(BaseModel):
    prompt: str
    model_type: str  # "new" or "recolor"
    user_email: str

orders = {}

# Root
@app.get("/")
def root():
    return {"message": "✅ Upland Kart API running!"}

# Create order
@app.post("/create-order")
def create_order(order: Order):
    order_id = str(uuid.uuid4())

    # Generate the final files based on prompt
    lod_files = generate_lods(order.prompt)
    nft_file = generate_nft(order.prompt)
    background_file = generate_background(order.prompt)

    # Save order
    orders[order_id] = {
        "prompt": order.prompt,
        "model_type": order.model_type,
        "user_email": order.user_email,
        "status": "ready",
        "files": {
            "LOD0": lod_files[0],
            "LOD1": lod_files[1],
            "LOD2": lod_files[2],
            "NFT": nft_file,
            "Background": background_file
        },
        "price": 120 if order.model_type == "new" else 30
    }

    return {"order_id": order_id, "status": "ready", "files": orders[order_id]["files"], "price": orders[order_id]["price"]}

# Check status
@app.get("/status/{order_id}")
def get_status(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order_id": order_id, "status": orders[order_id]["status"], "files": orders[order_id]["files"]}

# --- Helper functions ---

def generate_lods(prompt):
    """
    Placeholder: generate LOD0, LOD1, LOD2 GLTF files ≤ 20k triangles
    Returns a list of filenames
    """
    lod0 = f"lod0_{uuid.uuid4()}.gltf"
    lod1 = f"lod1_{uuid.uuid4()}.gltf"
    lod2 = f"lod2_{uuid.uuid4()}.gltf"
    # For now copy a template LOD (replace with AI generation later)
    for src, dst in [("lod_0_gltf.gltf", lod0), ("lod_1_gltf.gltf", lod1), ("lod_2_gltf.gltf", lod2)]:
        shutil.copyfile(src, dst)
    return [lod0, lod1, lod2]

def generate_nft(prompt):
    """
    Placeholder: generate NFT GLTF ≤ 10MB with carbody + wheel meshes
    """
    dst = f"nft_{uuid.uuid4()}.gltf"
    shutil.copyfile("nft_fullscreen_gltf.gltf", dst)
    return dst

def generate_background(prompt):
    """
    Placeholder: generate PNG background
    """
    dst = f"background_{uuid.uuid4()}.png"
    shutil.copyfile("background_template.png", dst)
    return dst
