from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import logging
import json

from .models import Base, UserInfoJP, UserInfoUS

DB_URL = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}?charset=utf8mb4&collation=utf8mb4_general_ci"


class RonnyaDB:
    def __init__(self):
        self.log("DB Initialization started.")
        self.engine = create_engine(DB_URL)
        Base.metadata.create_all(self.engine)

        self.sessionmaker = sessionmaker(bind=self.engine)

        self.log("DB Initialization done.")

    def read_data(self, fid: str, server: str) -> dict | None:
        self.log(
            "(FID: " + fid + ", server: " + server + ") Checking existence in DB..."
        )

        if server == "jp":
            UserInfo = UserInfoJP
        elif server == "us":
            UserInfo = UserInfoUS
        else:
            raise ValueError("Invalid server")

        with self.sessionmaker() as session:
            result = session.query(UserInfo).filter(UserInfo.fid == fid).first()

            if isinstance(result, UserInfo):
                self.log("(FID: " + fid + ") Found.")
                return result.__dict__
            else:
                self.log("(FID: " + fid + ") Not found.")
                return None

    def update_data(self, fid: str, data: dict, server: str) -> None:
        self.log("(FID: " + fid + ", server: " + server + ") Updating data...")
        data.update({"fid": fid, "last_update": datetime.now()})

        if server == "jp":
            UserInfo = UserInfoJP
        elif server == "us":
            UserInfo = UserInfoUS
        else:
            raise ValueError("Invalid server")

        with self.sessionmaker() as session:
            exist = (
                session.query(UserInfo).filter(UserInfo.fid == fid).first() is not None
            )

            try:
                if exist:
                    session.query(UserInfo).filter(UserInfo.fid == fid).update(data)
                else:
                    session.add(UserInfo(**data))
            except:
                session.rollback()
                raise
            else:
                session.commit()

        self.log("(FID: " + fid + ") Data updated.")

    @staticmethod
    def ws_to_db(data: dict) -> dict:
        result = {
            "uid": data["account_id"],
            "name": data["nickname"],
            "rank4": data["level"]["id"],
            "score4": data["level"]["score"],
            "rank3": data["level3"]["id"],
            "score3": data["level3"]["score"],
        }
        return result

    def log(self, msg: str) -> None:
        logging.info("[" + datetime.now().isoformat() + "] " + msg)


def main():
    print("----- Manual mode -----")
    r = RonnyaDB()

    while True:
        print("> ", end="")
        cmd = input().strip().split()
        if len(cmd) == 0:
            continue
        if cmd[0] == "stop":
            break
        elif cmd[0] == "read":
            print(r.read_data(str(cmd[1]), str(cmd[2])))
        elif cmd[0] == "update":
            r.update_data(str(cmd[1]), json.loads(cmd[3]), str(cmd[2]))
        else:
            print("No such command: " + cmd[0])


if __name__ == "__main__":
    main()
