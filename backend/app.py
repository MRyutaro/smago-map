import json
import os
from datetime import datetime
from enum import Enum

import dotenv
import requests
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from geopy.distance import geodesic
from pydantic import BaseModel

from database import test_connection

dotenv.load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
ROUTE_JSON_PATH = "./dummy_data/sample_route.json"
TRASHCANS_JSON_PATH = "./dummy_data/trashcans.json"
TRASHCANS_REQUESTS_JSON_PATH = "./dummy_data/trashcan_requests.json"
ROUTE_REQUESTS_HISTORY_JSON_PATH = "./dummy_data/route_requests_history.json"
R = 5000  # m
REQUEST_INTERVAL = 60  # min
# 1週間で10回までリクエスト可能
ROUTE_REQUEST_LIMIT = 100
ROUTE_REQUEST_INTERVAL = 7 * 24 * 60  # min


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
try:
    with open(TRASHCANS_JSON_PATH, "r", encoding="utf-8") as f:
        TRASHCANS = json.load(f)

    with open(TRASHCANS_REQUESTS_JSON_PATH, "r", encoding="utf-8") as f:
        TRASHCANS_REQUESTS = json.load(f)

    with open(ROUTE_REQUESTS_HISTORY_JSON_PATH, "r", encoding="utf-8") as f:
        ROUTE_REQUESTS_HISTORY = json.load(f)
except Exception as e:
    raise Exception(f"Error loading dummy data: {str(e)}")


@app.get("/api")
async def hello_api():
    try:
        return JSONResponse(content={"message": "Hello, API!"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


@app.get("/api/database")
async def hello_database():
    try:
        db_name = test_connection()
        return JSONResponse(content={"message": f"Hello, {db_name} database!"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


@app.get("/api/trashcans")
async def get_trashcans():
    try:
        # removed以外のゴミ箱のみを返す
        active_trashcans = [trashcan for trashcan in TRASHCANS if trashcan["status"] != "removed"]
        return JSONResponse(content={"trashcans": active_trashcans})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


@app.get("/api/requests")
async def get_requests():
    try:
        return JSONResponse(content={"requests": TRASHCANS_REQUESTS})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


@app.post("/api/requests")
async def create_request(trashcan_request: TrashcanRequest, request: Request):
    try:
        new_id = len(TRASHCANS_REQUESTS) + 1
        request_ip = request.client.host

        # IPアドレスごとにREQUEST_INTERVAL以内にリクエストがあるかチェック
        for req in TRASHCANS_REQUESTS:
            if req["host"] == request_ip:
                created_at = datetime.fromisoformat(req["created_at"])
                if (datetime.now() - created_at).total_seconds() < REQUEST_INTERVAL * 60:
                    return JSONResponse(content={"error": "Too many requests", "interval": REQUEST_INTERVAL}, status_code=429)

        new_request = {
            "id": new_id,
            "latitude": trashcan_request.latitude,
            "longitude": trashcan_request.longitude,
            "created_at": datetime.now().isoformat(),
            "host": request_ip,
        }
        TRASHCANS_REQUESTS.append(new_request)
        return JSONResponse(content={"message": "Request created", "request": new_request})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


@app.post("/api/route")
async def get_shortest_route(route_request: RouteRequest, request: Request):
    try:
        # リクエスト元のIPアドレスを取得
        request_ip = request.client.host

        # IPアドレスごとにROUTE_REQUEST_INTERVAL以内にリクエストがあるかチェック
        now = datetime.now()
        recent_requests = [
            req for req in ROUTE_REQUESTS_HISTORY
            if req["ip_address"] == request_ip and (now - datetime.fromisoformat(req["reqested_at"])).total_seconds() <= ROUTE_REQUEST_INTERVAL * 60
        ]
        if len(recent_requests) >= ROUTE_REQUEST_LIMIT:
            return JSONResponse(content={"error": "Too many requests"}, status_code=429)

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
        #     return JSONResponse(content={"error": "Full trashcans not found"}, status_code=404)

        # # ゴミ箱の位置をWaypointsとして構築
        # waypoints = "|".join([f'{t["latitude"]},{t["longitude"]}' for t in filtered_trashcans])

        # # Google Maps Directions APIエンドポイント
        # mode = "walking"  # "driving", "walking", "bicycling", "transit"
        # url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints={waypoints}&key={GOOGLE_MAPS_API_KEY}&mode={mode}"

        # response = requests.get(url)
        # if response.status_code != 200:
        #     return JSONResponse(content={"error": "Error fetching route from Google API"}, status_code=400)

        # route_data = response.json()

        # ファイルから読み込む場合
        with open(ROUTE_JSON_PATH, "r", encoding="utf-8") as f:
            route_data = json.load(f)

        # print(route_data)

        polyline_points = route_data["routes"][0]["overview_polyline"]["points"]

        # リクエスト履歴に追加
        ROUTE_REQUESTS_HISTORY.append({
            "id": len(ROUTE_REQUESTS_HISTORY) + 1,
            "ip_address": request_ip,
            "reqested_at": now.isoformat()
        })

        return JSONResponse(content={"radius": R, "polyline_points": polyline_points})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
