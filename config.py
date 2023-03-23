from pydantic import BaseModel
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["settings"]["TOKEN"]
BOT_NAME = config["settings"]["BOT_NAME"]
SUPPORT_NAME = config["settings"]["SUPPORT_NAME"]
ADMINS = config["settings"]["admins"].split(",")
ADMINS = [int(admin) for admin in ADMINS]
video_1 = config["settings"]["video_1"]
video_2 = config["settings"]["video_2"]
pay_token = config["settings"]["pay_token"]


class DB(BaseModel):
    user = config["db"]["user"]
    password = config["db"]["password"]
    database = config["db"]["database"]
    host = config["db"]["host"]
    port = config["db"]["port"]


SQLALCHEMY_DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{database}".format(**DB().dict())
