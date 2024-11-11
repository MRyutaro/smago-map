import json
import os
from datetime import datetime
from enum import Enum

import dotenv
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

dotenv.load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
ROUTE_PATH = "./sample_route.json"

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Request(BaseModel):
    latitude: float
    longitude: float


# statusのenumを定義
class Status(str, Enum):
    full = "full"
    not_full = "not_full"
    removed = "removed"


# ダミーデータ
TRASHCANS = [
    {"id": 1, "latitude": 35.7137757, "longitude": 139.7969451, "location_description": "近くの公園に設置してあります", "status": Status.full},
    {"id": 2, "latitude": 35.7143071, "longitude": 139.7963245, "location_description": "近くの交差点に設置してあります", "status": Status.not_full},
    {"id": 3, "latitude": 35.7144253, "longitude": 139.7953445, "location_description": "近くの駅に設置してあります", "status": Status.removed},
    {"id": 4, "latitude": 35.714748, "longitude": 139.7952627, "location_description": "近くの商店街に設置してあります", "status": Status.full},
    {"id": 5, "latitude": 35.7111474, "longitude": 139.7965377, "location_description": "近くの学校に設置してあります", "status": Status.full},
    {"id": 6, "latitude": 35.7119654, "longitude": 139.7963265, "location_description": "近くの図書館に設置してあります", "status": Status.removed},
    {"id": 7, "latitude": 35.7124165, "longitude": 139.7963355, "location_description": "近くの公民館に設置してあります", "status": Status.full},
    {"id": 8, "latitude": 35.7128409, "longitude": 139.7963711, "location_description": "近くの病院に設置してあります", "status": Status.not_full},
    {"id": 9, "latitude": 35.7128488, "longitude": 139.7960204, "location_description": "近くのスーパーに設置してあります", "status": Status.full},
    {"id": 10, "latitude": 35.7112601, "longitude": 139.7963721, "location_description": "近くのコンビニに設置してあります", "status": Status.full},
]

REQUESTS = [
    {"id": 1, "latitude": 35.71279354903134, "longitude": 139.79717373847964, "created_at": "2024-11-11T12:00:00.910987"},
    {"id": 2, "latitude": 35.7132465360125, "longitude": 139.79656219482425, "created_at": "2024-11-11T12:30:00.627615"},
]


@app.get("/api")
async def read_root():
    return {"Hello": "World"}


@app.get("/api/trashcans")
async def get_trashcans():
    # removed以外のゴミ箱のみを返す
    active_trashcans = [trashcan for trashcan in TRASHCANS if trashcan["status"] != Status.removed]
    return {"trashcans": active_trashcans}


@app.get("/api/requests")
async def get_requests():
    return {"requests": REQUESTS}


@app.post("/api/requests")
async def create_request(request: Request):
    new_id = len(REQUESTS) + 1
    new_request = {
        "id": new_id,
        "latitude": request.latitude,
        "longitude": request.longitude,
        "created_at": datetime.now().isoformat(),
    }
    REQUESTS.append(new_request)
    return {"request": new_request}


@app.get("/api/route")
async def get_shortest_route():
    # # full状態のゴミ箱のみを抽出
    # full_trashcans = [trashcan for trashcan in TRASHCANS if trashcan["status"] == Status.full]

    # if not full_trashcans:
    #     raise HTTPException(status_code=404, detail="Full trashcans not found")

    # # ゴミ箱の位置をWaypointsとして構築
    # waypoints = "|".join([f'{t["latitude"]},{t["longitude"]}' for t in full_trashcans])

    # # 最初と最後のゴミ箱位置（例：1番目と最後のゴミ箱位置に設定）
    # origin = f'{full_trashcans[0]["latitude"]},{full_trashcans[0]["longitude"]}'
    # destination = f'{full_trashcans[-1]["latitude"]},{full_trashcans[-1]["longitude"]}'

    # # Google Maps Directions APIエンドポイント
    # url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints={waypoints}&key={GOOGLE_MAPS_API_KEY}"

    # response = requests.get(url)
    # if response.status_code != 200:
    #     raise HTTPException(status_code=response.status_code, detail="Error fetching route from Google API")

    # route_data = response.json()
    with open(ROUTE_PATH, "r", encoding="utf-8") as f:
        route_data = json.load(f)

    polyline_points = route_data["routes"][0]["overview_polyline"]["points"]
    return {"polyline_points": polyline_points}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
