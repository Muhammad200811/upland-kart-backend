from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://upland-kart-studio-b82351ca.base44.app"],  # Base44 frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Order(BaseModel):
    prompt: str
    model_type: str  # "new" or "recolor"
    user_email: str

orders = {}

@app.post("/create-order")
def create_order(order: Order):
    order_id = str(uuid.uuid4())
    orders[order_id] = {
        "prompt": order.prompt,
        "model_type": order.model_type,
        "user_email": order.user_email,
        "status": "pending",
        "price": 120 if order.model_type == "new" else 30
    }
    return {"order_id": order_id, "price": orders[order_id]["price"]}

@app.get("/status/{order_id}")
def get_status(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order_id": order_id, "status": orders[order_id]["status"]}

@app.post("/complete-order/{order_id}")
def complete_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    orders[order_id]["status"] = "ready"
    return {"order_id": order_id, "status": "ready"}

    }
