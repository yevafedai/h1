import datetime as dt
import json

import requests
from flask import Flask, jsonify, request
from datetime import datetime

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "tokenFromMe112"
# you can get API keys for free here - https://api-docs.pgamerx.com/
RSA_API_KEY = "afee634312744607adb45804232302"

app = Flask(__name__)


def generate_weather(location: str, startdata: str, lang: str):
    url_base_url = "http://api.weatherapi.com"
    url_api = "v1"
    url_endpoint = ""
    url_exclude = ""
    url_location = ""
    url_startdata = ""
    url_lang = ""
    url_key = f"?key={RSA_API_KEY}"
    date_datatime = datetime.strptime(startdata, "%Y-%m-%d")
    now = datetime.now()

    if date_datatime.date() == now.date():
        url_endpoint = "current.json"
    elif date_datatime.date() < now.date():
        url_endpoint = "history.json"
    else:
        url_endpoint = "future.json"

    if location:
        url_location = f"&q={location}"

    if startdata:
        url_startdata = f"&dt={startdata}"

    if lang:
        url_lang = f"&lang={lang}"

    url = f"{url_base_url}/{url_api}/{url_endpoint}{url_key}{url_location}{url_startdata}{url_lang}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def weather_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    requestername = ""
    if json_data.get("requester_name"):
        requestername = json_data.get("requester_name")

    location = ""
    if json_data.get("location"):
        location = json_data.get("location")

    lang = ""
    if json_data.get("lang"):
        lang = json_data.get("lang")

    startdata = ""
    if json_data.get("data"):
        startdata = json_data.get("data")

    weather = generate_weather(location, startdata, lang)
    end_dt = dt.datetime.now()

    result = {
        "event_start_datetime": start_dt.isoformat(),
        "event_finished_datetime": end_dt.isoformat(),
        "event_duration": str(end_dt - start_dt),
        "requester_name": requestername,
        "weather": weather,
    }

    return result
