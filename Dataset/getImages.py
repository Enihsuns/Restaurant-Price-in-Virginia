import urllib.request
import json

from urllib.error import HTTPError

biz_json_file = "./restaurants_VA.json"

with open(biz_json_file, 'r', encoding='utf8') as inFile:
    businesses = json.load(inFile)

for biz in businesses:
    biz_id = biz["id"]
    image_url = biz["image_url"]
    if image_url == "":
        continue
    opener = urllib.request.URLopener()
    try:
        opener.retrieve(image_url, "./Images/" + biz_id + ".jpg")
    except HTTPError as error:
        continue