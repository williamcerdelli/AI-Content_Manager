import requests, json

from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("NOTION_API_KEY")

databaseID = '932b90e793db484f93daaf2bda259819'
headers = {
    "Authorization": "Bearer " + token,
    "Notion-Version": "2022-06-28"

}


def readDatabse(databaseID, headers):
    readUrl = f"https://api.notion.com/v1/databases/{databaseID}"

    res = requests.request("GET", readUrl, headers=headers)
    print(res.text)


def createPage():
    pass


def updatePage():
    pass


readDatabse(databaseID, headers)