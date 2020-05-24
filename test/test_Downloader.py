import sys, os
test_dir = os.path.dirname(__file__)
src_dir = '../code'
sys.path.insert(0, os.path.abspath(os.path.join(test_dir, src_dir)))
from unittest import TestCase
from unittest.mock import MagicMock, patch
import json
import asyncio
import requests
from code import Downloader

TEST_DATA_SENSOR_IDS = {'_id': 'b123', 'sensors': [{'_id': 'x1'}, {'_id': 'y1'}, {'_id': 'z1'}]}
TEST_DATA_REQ_RESULT = [{"value":"5.43","location":[7.854577,47.993157],"createdAt":"2020-05-19T11:48:58.629Z"},
                        {"value":"5.68","location":[7.854577,47.993157],"createdAt":"2020-05-19T11:43:58.629Z"},
                        {"value":"5.65","location":[7.854577,47.993157],"createdAt":"2020-05-19T11:38:58.629Z"}]

class TestDownloader(TestCase):
    ##############################
    # test for get_sensors_id
    ##############################
    def test_get_sensors_id_success(self):
        expected = ["x1", "y1", "z1"]
        result = Downloader.get_sensors_id(json.dumps(TEST_DATA_SENSOR_IDS).encode('utf-8'))
        assert result == expected

    def test_get_sensors_id_failed(self):
        self.assertRaises(expected_exception=TypeError, callable=Downloader.get_sensors_id, vars={})

    ##############################
    # test for read_hist_from_src
    ##############################
    def test_read_hist_from_src_success(self):
        val = json.dumps(TEST_DATA_REQ_RESULT).encode('utf-8')
        Downloader.request_data = MagicMock(return_value={"key": "x", "value": val})
        loop = asyncio.get_event_loop()
        task = loop.create_task(Downloader.read_hist_from_src("x", "y"))
        loop.run_until_complete(task)
        result = task.result()
        assert val == result["value"]

    def test_read_hist_from_src_failed(self):
        Downloader.request_data = MagicMock(return_value={})
        loop = asyncio.get_event_loop()
        task = loop.create_task(Downloader.read_hist_from_src("x", None))  # Unproccesing Entity
        loop.run_until_complete(task)
        result = task.result()
        assert not result

    ##############################
    # test for read_from_src
    ##############################
    def test_read_from_src_success(self):
        val = json.dumps([TEST_DATA_REQ_RESULT]).encode('utf-8')
        Downloader.request_data = MagicMock(return_value={"key": "x", "value": val})
        loop = asyncio.get_event_loop()
        task = loop.create_task(Downloader.read_from_src("x"))
        loop.run_until_complete(task)
        result = task.result()
        assert result["key"] == "x"

    def test_read_from_src_failed(self):
        Downloader.request_data = MagicMock(return_value={})
        loop = asyncio.get_event_loop()
        task = loop.create_task(Downloader.read_from_src(None))  # Unproccesing Entity
        loop.run_until_complete(task)
        result = task.result()
        assert not result

    ##############################
    # test for request_data
    ##############################
    @patch("Downloader.requests.get")
    def test_request_data_success(self, mock_get):
        expected_key = "x"
        mock_get.return_value.ok = True
        result = Downloader.request_data("x", "http://fake_url")
        assert  result["key"] == expected_key

    @patch("Downloader.requests.get")
    def test_request_data_failed(self, mock_get):
        mock_get.return_value = requests.exceptions.MissingSchema()
        self.assertRaises(expected_exception=requests.exceptions.MissingSchema,
                          callable=Downloader.request_data, vars=["x", "fake_url"])

    @patch("Downloader.requests.get")
    def test_request_data_timeout(self, mock_get):
        expected_key = "x"
        mock_get.return_value = requests.exceptions.Timeout()
        self.assertRaises(expected_exception=requests.exceptions.Timeout,
                          callable=Downloader.request_data, vars=["x", "fake_url"])

    @patch("Downloader.requests.get")
    def test_request_data_connection_error(self, mock_get):
        expected_key = "x"
        mock_get.return_value = requests.exceptions.ConnectionError()
        self.assertRaises(expected_exception=requests.exceptions.ConnectionError,
                          callable=Downloader.request_data, vars=["x", "fake_url"])
