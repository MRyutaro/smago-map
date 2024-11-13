import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


# 環境変数から取得
# IS_DOCKERは0か1の値を取る
IS_DOCKER = os.getenv("IS_DOCKER")

if IS_DOCKER == "1":
    POSTGRES_USER = os.getenv("DOCKER_POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("DOCKER_POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("DOCKER_POSTGRES_HOST")
    POSTGRES_DB = os.getenv("DOCKER_POSTGRES_DB")
    ENGINE = create_engine(
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"
    )
else:
    DB_NAME = "smago-map"
    # sqlite
    ENGINE = create_engine(f"sqlite:///{DB_NAME}.sqlite3")


# ENGINEに接続できるか確認
def test_connection():
    try:
        with ENGINE.connect():
            print("DBとの接続に成功しました")
            # postgresかsqliteかを返す
            return ENGINE.dialect.name
    except Exception as e:
        print("DBとの接続に失敗しました")
        print(e)


if __name__ == "__main__":
    if test_connection():
        print("接続成功")
    else:
        print("接続失敗")
