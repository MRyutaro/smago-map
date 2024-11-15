import json
import os
from datetime import datetime
from enum import Enum

import dotenv
import requests
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from geopy.distance import geodesic
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from database import test_connection

dotenv.load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
ROUTE_JSON_PATH = "./dummy_data/sample_route.json"
TRASHCANS_JSON_PATH = "./dummy_data/trashcans.json"
TRASHCANS_REQUESTS_JSON_PATH = "./dummy_data/trashcan_requests.json"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET")

# 上の4つのいずれかがNoneの場合はエラー
if None in [GOOGLE_MAPS_API_KEY, ROUTE_JSON_PATH, TRASHCANS_JSON_PATH, TRASHCANS_REQUESTS_JSON_PATH]:
    raise ValueError("Please set the environment variables")


app = FastAPI()

# セッションミドルウェアを追加
app.add_middleware(SessionMiddleware, secret_key="your_session_secret_key")

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


oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
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


# Google OAuth認証エンドポイント
@app.get("/auth/login")
async def login_via_google(request: Request):
    try:
        redirect_uri = GOOGLE_REDIRECT_URI
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/auth/callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        return JSONResponse({"message": "Authentication successful", "user": user_info})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


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
                    raise HTTPException(status_code=429, detail="Too many requests")

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
async def get_shortest_route(route_request: RouteRequest):
    try:
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

        return JSONResponse(content={"radius": R, "polyline_points": polyline_points})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)    


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
