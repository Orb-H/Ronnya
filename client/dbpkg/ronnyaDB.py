from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import logging
import json

from .models import UserInfo, Base

DB_URL = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}?charset=utf8mb4&collation=utf8mb4_general_ci"


class RonnyaDB:
    def __init__(self):
        self.log("DB Initialization started.")
        self.engine = create_engine(DB_URL)
        Base.metadata.create_all(self.engine)

        self.sessionmaker = sessionmaker(bind=self.engine)

        self.log("DB Initialization done.")

    def read_data(self, fid: str) -> dict | None:
        self.log("(FID: " + fid + ") Checking existence in DB...")

        with self.sessionmaker() as session:
            result = session.query(UserInfo).filter(UserInfo.fid == fid).first()

            if isinstance(result, UserInfo):
                self.log("(FID: " + fid + ") Found.")
                return result.__dict__
            else:
                self.log("(FID: " + fid + ") Not found.")
                return None

    def update_data(self, fid: str, data: dict) -> None:
        self.log("(FID: " + fid + ") Updating data...")
        data.update({"fid": fid, "last_update": datetime.now()})

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

    def log(self, msg: str) -> None:
        logging.info("[" + datetime.now().isoformat() + "] " + msg)
