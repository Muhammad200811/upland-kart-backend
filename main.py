from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from PIL import Image
import shutil
import uuid
import os

# ✅ Automatically create folders if missing
os.makedirs("templates", exist_ok=True)
os.makedirs("generated", exist_ok=True)

app = FastAPI()

# ✅ Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing; later restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧩 Order schema
class Order(BaseModel):
    prompt: str
    model_type: str
    user_email: str

# 🗂️ In-memory order store (temporary)
orders = {}

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
GENERATED_DIR = BASE_DIR / "generated"

# 🧠 Generate textures and copy GLTF templates
def generate_texture(order_id: str, prompt: str):
    out_dir = GENERATED_DIR / order_id
    out_dir.mkdir(exist_ok=True)

    # Simple placeholder texture
    color = abs(hash(prompt)) % 0xFFFFFF
    img = Image.new("RGB", (1024, 1024), color=f"#{color:06x}")
    img.save(out_dir / "LOD0_texture.jpg")

    # Copy template 3D files
    if (TEMPLATES_DIR / "lod_0_gltf.gltf").exists():
        shutil.copy(TEMPLATES_DIR / "lod_0_gltf.gltf", out_dir / "LOD0.gltf")
        shutil.copy(TEMPLATES_DIR / "lod_1_gltf.gltf", out_dir / "LOD1.gltf")
        shutil.copy(TEMPLATES_DIR / "lod_1_texture.jpg", out_dir / "LOD1_texture.jpg")
        shutil.copy(TEMPLATES_DIR / "lod_2_gltf.gltf", out_dir / "LOD2.gltf")
        shutil.copy(TEMPLATES_DIR / "lod_2_texture.jpg", out_dir / "LOD2_texture.jpg")
        shutil.copy(TEMPLATES_DIR / "nft_fullscreen_gltf.gltf", out_dir / "NFT_fullscreen.gltf")
        shutil.copy(TEMPLATES_DIR / "nft_ipfs_gltf.gltf", out_dir / "NFT_IPFS.gltf")
        shutil.copy(TEMPLATES_DIR / "nft_texture_wheel.jpg", out_dir / "NFT_texture_wheel.jpg")
        shutil.copy(TEMPLATES_DIR / "nft_ipfs.png", out_dir / "background.png")

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

    # Run process in the background
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


# 🛠️ Generate and mark order as ready
def process_order(order_id: str):
    order = orders[order_id]
    prompt = order["prompt"]
    generated_dir = generate_texture(order_id, prompt)

    files = {f.name: str(f) for f in generated_dir.iterdir()}
    orders[order_id]["files"] = files
    orders[order_id]["status"] = "ready"
