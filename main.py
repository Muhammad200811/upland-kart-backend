from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os

app = FastAPI(title="Upland GoKart Generator API")

# Base44 frontend domain
FRONTEND_URL = "https://upland-kart-studio-b82351ca.base44.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Order(BaseModel):
    prompt: str
    model_type: str  # "new" or "recolor"
    user_email: str

orders = {}

# Placeholder AI function
def generate_gokart_files(order_id, prompt, model_type):
    output_folder = f"generated/{order_id}"
    os.makedirs(output_folder, exist_ok=True)
    files = {
        "LOD0": f"{output_folder}/LOD0.glb",
        "LOD1": f"{output_folder}/LOD1.glb",
        "LOD2": f"{output_folder}/LOD2.glb",
        "GLTF": f"{output_folder}/gokart.gltf",
        "NFT_BG": f"{output_folder}/background.png",
    }
    for f in files.values():
        with open(f, "w") as fp:
            fp.write(f"Simulated file for {order_id} - {prompt}")
    return files

@app.post("/create-order")
def create_order(order: Order):
    order_id = str(uuid.uuid4())
    price = 120 if order.model_type == "new" else 30
    orders[order_id] = {
        "prompt": order.prompt,
        "model_type": order.model_type,
        "user_email": order.user_email,
        "status": "pending",
        "price": price,
        "files": None
    }

    # Generate files (simulate AI)
    files = generate_gokart_files(order_id, order.prompt, order.model_type)
    orders[order_id]["files"] = files
    orders[order_id]["status"] = "ready"  # change to pending if async

    return {"order_id": order_id, "price": price}

@app.get("/status/{order_id}")
def get_status(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order_id": order_id,
        "status": orders[order_id]["status"],
        "files": orders[order_id]["files"] if orders[order_id]["status"] == "ready" else None
    }

@app.post("/complete-order/{order_id}")
def complete_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    orders[order_id]["status"] = "ready"
    return {"order_id": order_id, "status": "ready"}

@app.get("/")
def health_check():
    return {"message": "✅ Upland Kart API is running correctly!"}
