from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid, os, shutil
from pathlib import Path
from PIL import Image

app = FastAPI()

# ⚠️ CORS must be first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Order(BaseModel):
    prompt: str
    model_type: str
    user_email: str

orders = {}

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

def generate_texture(order_id, prompt):
    out_dir = GENERATED_DIR / order_id
    out_dir.mkdir(exist_ok=True)
    
    # Placeholder color for demonstration
    color = abs(hash(prompt)) % 0xFFFFFF
    img = Image.new("RGB", (1024, 1024), color=f"#{color:06x}")
    img.save(out_dir / "LOD0_texture.jpg")
    
    # Copy template files
    template_files = [
        ("lod_0_gltf.gltf", "LOD0.gltf"),
        ("lod_1_gltf.gltf", "LOD1.gltf"),
        ("lod_1_texture.jpg", "LOD1_texture.jpg"),
        ("lod_2_gltf.gltf", "LOD2.gltf"),
        ("lod_2_texture.jpg", "LOD2_texture.jpg"),
        ("nft_fullscreen_gltf.gltf", "NFT_fullscreen.gltf"),
        ("nft_ipfs_gltf.gltf", "NFT_IPFS.gltf"),
        ("nft_texture_wheel.jpg", "NFT_texture_wheel.jpg"),
        ("nft_ipfs.png", "background.png"),
    ]
    
    for src_name, dst_name in template_files:
        src_file = TEMPLATES_DIR / src_name
        dst_file = out_dir / dst_name
        if src_file.exists():
            shutil.copy(src_file, dst_file)
    
    img.save(out_dir / "NFT_texture_carbody.jpg")
    return out_dir

@app.get("/")
def root():
    return {"message": "✅ Upland Kart API is running correctly!"}

@app.post("/create-order")
async def create_order(order: Order, background_tasks: BackgroundTasks):
    order_id = str(uuid.uuid4())
    price = 120 if order.model_type == "new" else 30
    orders[order_id] = {
        "prompt": order.prompt,
        "model_type": order.model_type,
        "user_email": order.user_email,
        "status": "pending",
        "price": price
    }
    
    background_tasks.add_task(process_order, order_id)
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

def process_order(order_id):
    order = orders[order_id]
    prompt = order["prompt"]
    generated_dir = generate_texture(order_id, prompt)
    
    files = {f.stem: str(f) for f in generated_dir.iterdir()}
    orders[order_id]["files"] = files
    orders[order_id]["status"] = "ready"

