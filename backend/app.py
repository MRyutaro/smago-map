import json
import os
from datetime import datetime
from enum import Enum

import dotenv
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from geopy.distance import geodesic
from pydantic import BaseModel

from database import test_connection


dotenv.load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
ROUTE_JSON_PATH = "./dummy_data/sample_route.json"
TRASHCANS_JSON_PATH = "./dummy_data/trashcans.json"
TRASHCANS_REQUESTS_JSON_PATH = "./dummy_data/trashcan_requests.json"

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


class TrashcanRequest(BaseModel):
    latitude: float
    longitude: float


class Location(BaseModel):
    latitude: float
    longitude: float


class RouteRequest(BaseModel):
    origin: Location
    destination: Location


# ダミーデータ
with open(TRASHCANS_JSON_PATH, "r", encoding="utf-8") as f:
    TRASHCANS = json.load(f)

with open(TRASHCANS_REQUESTS_JSON_PATH, "r", encoding="utf-8") as f:
    TRASHCANS_REQUESTS = json.load(f)

R = 5000  # m

REQUEST_INTERVAL = 60  # min


@app.get("/api")
async def hello_api():
    return {"message": "Hello, API!"}


@app.get("/api/database")
async def hello_database():
    db_name = test_connection()
    return {"message": f"Hello, {db_name} database!"}


@app.get("/api/trashcans")
async def get_trashcans():
    # removed以外のゴミ箱のみを返す
    active_trashcans = [trashcan for trashcan in TRASHCANS if trashcan["status"] != "removed"]
    return {"trashcans": active_trashcans}


@app.get("/api/requests")
async def get_requests():
    return {"requests": TRASHCANS_REQUESTS}


@app.post("/api/requests")
async def create_request(trashcan_request: TrashcanRequest, request: Request):
    new_id = len(TRASHCANS_REQUESTS) + 1
    request_ip = request.client.host

    # IPアドレスごとにREQUEST_INTERVAL以内にリクエストがあるかチェック
    for req in TRASHCANS_REQUESTS:
        if req["host"] == request_ip:
            created_at = datetime.fromisoformat(req["created_at"])
            if (datetime.now() - created_at).total_seconds() < REQUEST_INTERVAL * 60:
                raise HTTPException(status_code=429, detail="Too many requests")

    new_request = {
        "id": new_id,
        "latitude": trashcan_request.latitude,
        "longitude": trashcan_request.longitude,
        "created_at": datetime.now().isoformat(),
        "host": request_ip,
    }
    TRASHCANS_REQUESTS.append(new_request)
    return {"request": new_request}


@app.post("/api/route")
async def get_shortest_route(route_request: RouteRequest):
    # # 最初と最後のゴミ箱位置（例：1番目と最後のゴミ箱位置に設定）
    # origin = f'{route_request.origin.latitude},{route_request.origin.longitude}'
    # destination = f'{route_request.destination.latitude},{route_request.destination.longitude}'
    # # origin = '35.72285883534467,139.80149745941165'
    # # destination = '35.72285883534467,139.80149745941165'

    # # 半径 R 以内のゴミ箱をフィルタリング
    # filtered_trashcans = [
    #     trashcan for trashcan in TRASHCANS
    #     if geodesic(origin, (trashcan["latitude"], trashcan["longitude"])).meters <= R
    # ]

    # if not filtered_trashcans:
    #     raise HTTPException(status_code=404, detail="Full trashcans not found")

    # # ゴミ箱の位置をWaypointsとして構築
    # waypoints = "|".join([f'{t["latitude"]},{t["longitude"]}' for t in filtered_trashcans])

    # # Google Maps Directions APIエンドポイント
    # mode = "walking"  # "driving", "walking", "bicycling", "transit"
    # url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints={waypoints}&key={GOOGLE_MAPS_API_KEY}&mode={mode}"

    # response = requests.get(url)
    # if response.status_code != 200:
    #     raise HTTPException(status_code=response.status_code, detail="Error fetching route from Google API")

    # route_data = response.json()

    # ファイルから読み込む場合
    with open(ROUTE_JSON_PATH, "r", encoding="utf-8") as f:
        route_data = json.load(f)

    # print(route_data)

    polyline_points = route_data["routes"][0]["overview_polyline"]["points"]
    return {
        "radius": R,
        "polyline_points": polyline_points
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
