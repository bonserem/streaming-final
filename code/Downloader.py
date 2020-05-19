import requests
import asyncio
import time
import logging
import json
from datetime import datetime, timedelta

### Service Downloader (DataProducer) -> RowDataTopic

# const
BOXES_URL: str = "https://api.opensensemap.org/boxes/"
READ_INTERVAL: int = 10
HIST_LEAD_TIME: int = -60 # maximal historical lead time in minutes
ERR_UNEXPECTED: str = "unexpected error!"
ERR_REQ_CNN: str = "request connection error!"
ERR_REQ_TIMEOUT: str = "request timeout error!"
LOG_FORMAT: str = "%(asctime)s %(levelname)s: %(funcName)s -> %(message)s"
BOXES_CONFIG = [
    {
        "name": "PM Freiburg City Schlossbergring",
        "_id": "5b8449037c519100190fc728",
        "coordinates": [7.854577, 47.993157],
        "sensors": [{"_id": "5b8449037c519100190fc72c", "title": "PM10", "unit": "\u00b5g/m\u00b3"}]
    },
    {
        "name": "Leonhardsgraben",
        "_id": "5d76badc953683001aa283ef",
        "coordinates": [7.854577, 47.993157],
        "sensors": [{"_id": "5d76badc953683001aa283f5", "title": "PM10", "unit": "\u00b5g/m\u00b3"}]
    }]

# initialize logging
logging.basicConfig(filename=f"Downloader.log", format=LOG_FORMAT, filemode="w")
lg = logging.getLogger()
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
lg.addHandler(c_handler)

### Read historical data
# Request Data
def request_data(key, url):
    try:
        return {"key": key, "value": requests.get(url).content}
    except requests.exceptions.ConnectionError: lg.error(f"{ERR_REQ_CNN} <url: {url}>")
    except requests.exceptions.Timeout: lg.error(f"{ERR_REQ_TIMEOUT} <url: {url}>")

@asyncio.coroutine
async def read_hist_from_src(box_id, sensor_id):
    f_date = (datetime.utcnow() + timedelta(minutes=HIST_LEAD_TIME)).isoformat("T") + "Z"
    return request_data(sensor_id, f"{BOXES_URL}{box_id}/data/{sensor_id}?from_date={f_date}")

### Read current box data
@asyncio.coroutine
async def read_from_src(box_id): return request_data(box_id, f"{BOXES_URL}{box_id}")

### Write history to RawData(Kafka)
def write_to_raw_hist(h_data):
    # To do
    # for s in h_data: p.Produce("raw", key=s["key"], value=s["value], ...

    # debug
    for sensor in h_data:
        print(f"\nwrite sensor <{sensor['key']}> history data to raw hist producer...")
        val = sensor["value"]
        print(json.loads(val))
        # print(json.dumps(json.loads(val.decode()), sort_keys=True, indent=4))


### Write to RawData(Kafka)
def write_to_raw(data):
    # To do
    # for b in data: p.Produce("raw", key=data["key"], value=data["value], ...

    # debug
    for sensor in data:
        print(f"\nwrite sensor stream <{sensor['key']}> to raw producer...")
        val = sensor["value"]
        print(val.decode())
        # print(json.dumps(json.loads(val.decode()), sort_keys=True, indent=4))

def get_sensors_id(b_val): return [s["_id"] for s in json.loads(b_val)["sensors"]]

if __name__ == "__main__":
    print("Downloader is running, close with Ctrl+C")
    try:
        loop = asyncio.get_event_loop()
        while True:
            tasks = []
            for b in BOXES_CONFIG:
                sensors = b["sensors"]
                tasks.extend(iter([loop.create_task(read_hist_from_src(b["_id"], s["_id"])) for s in sensors]))
            loop.run_until_complete(asyncio.wait(tasks))
            result = [t.result() for t in tasks]
            write_to_raw(result)
            time.sleep(READ_INTERVAL)
    except:
        lg.critical(ERR_UNEXPECTED, exc_info=True)
