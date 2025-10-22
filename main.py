from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid, os, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import asyncio

app = FastAPI()

# ⚠️ CORS must be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class Order(BaseModel):
    prompt: str
    model_type: str  # "new" or "recolor"
    user_email: str

# In-memory orders storage
orders = {}

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

# ----------------- Helper Functions -----------------

def generate_texture(order_id, prompt):
    """
    Simulate AI texture generation using a placeholder image.
    Replace this with actual AI call (Stable Diffusion, etc.) later.
    """
    out_dir = GENERATED_DIR / order_id
    out_dir.mkdir(exist_ok=True)
    
    # Example: create a simple colored image based on prompt hash
    color = abs(hash(prompt)) % 0xFFFFFF
    img = Image.new("RGB", (1024, 1024), color=f"#{color:06x}")
    img.save(out_dir / "LOD0_texture.jpg")
    shutil.copy(TEMPLATES_DIR / "lod_0_gltf.gltf", out_dir / "LOD0.gltf")
    shutil.copy(TEMPLATES_DIR / "lod_1_gltf.gltf", out_dir / "LOD1.gltf")
    shutil.copy(TEMPLATES_DIR / "lod_1_texture.jpg", out_dir / "LOD1_texture.jpg")
    shutil.copy(TEMPLATES_DIR / "lod_2_gltf.gltf", out_dir / "LOD2.gltf")
    shutil.copy(TEMPLATES_DIR / "lod_2_texture.jpg", out_dir / "LOD2_texture.jpg")
    
    # NFT textures
    img.save(out_dir / "NFT_texture_carbody.jpg")
    shutil.copy(TEMPLATES_DIR / "nft_fullscreen_gltf.gltf", out_dir / "NFT_fullscreen.gltf")
    shutil.copy(TEMPLATES_DIR / "nft_ipfs_gltf.gltf", out_dir / "NFT_IPFS.gltf")
    shutil.copy(TEMPLATES_DIR / "nft_texture_wheel.jpg", out_dir / "NFT_texture_wheel.jpg")
    shutil.copy(TEMPLATES_DIR / "nft_ipfs.png", out_dir / "background.png")
    
    return out_dir

# ----------------- Routes -----------------

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
    
    # Trigger async generation
    asyncio.create_task(process_order(order_id))
    
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

async def process_order(order_id):
    """
    Generates textures and copies GLTF files asynchronously.
    """
    order = orders[order_id]
    prompt = order["prompt"]
    generated_dir = generate_texture(order_id, prompt)
    
    files = {f.stem: str(f) for f in generated_dir.iterdir()}
    orders[order_id]["files"] = files
    orders[order_id]["status"] = "ready"
