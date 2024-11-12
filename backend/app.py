import json
import os
from datetime import datetime
from enum import Enum

import dotenv
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from geopy.distance import geodesic
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


class Location(BaseModel):
    latitude: float
    longitude: float


class RouteRequest(BaseModel):
    origin: Location
    destination: Location


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
    {"id": 11, "latitude": 35.680916839441025, "longitude": 139.76553440093997, "location_description": "", "status": Status.full},
    {"id": 12, "latitude": 35.681962608079424, "longitude": 139.7661137580872, "location_description": "", "status": Status.not_full},
    {"id": 13, "latitude": 35.682746925563386, "longitude": 139.76675748825076, "location_description": "", "status": Status.not_full},
    {"id": 14, "latitude": 35.68107370561057, "longitude": 139.76450443267825, "location_description": "", "status": Status.not_full},
    {"id": 15, "latitude": 35.682136901519925, "longitude": 139.7646760940552, "location_description": "", "status": Status.not_full},
    {"id": 16, "latitude": 35.69341287787123, "longitude": 139.7714996337891, "location_description": "", "status": Status.full},
    {"id": 17, "latitude": 35.68692982193015, "longitude": 139.76909637451175, "location_description": "", "status": Status.full},
    {"id": 18, "latitude": 35.69250667592556, "longitude": 139.75948333740237, "location_description": "", "status": Status.full},
]

REQUESTS = [
    {"id": 1, "latitude": 35.71279354903134, "longitude": 139.79717373847964, "created_at": "2024-11-11T12:00:00.910987"},
    {"id": 2, "latitude": 35.7132465360125, "longitude": 139.79656219482425, "created_at": "2024-11-11T12:30:00.627615"},
]

R = 5000  # m


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
    # url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints={waypoints}&key={GOOGLE_MAPS_API_KEY}"

    # response = requests.get(url)
    # if response.status_code != 200:
    #     raise HTTPException(status_code=response.status_code, detail="Error fetching route from Google API")

    # route_data = response.json()

    # ファイルから読み込む場合
    with open(ROUTE_PATH, "r", encoding="utf-8") as f:
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
