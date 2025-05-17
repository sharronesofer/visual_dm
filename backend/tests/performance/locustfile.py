from locust import HttpUser, task, between, events
import gevent
import websocket
import json

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def api_worlds(self):
        self.client.get("/api/worlds")

    @task
    def api_npcs(self):
        self.client.get("/api/npcs")

    @task
    def ws_connect(self):
        ws = websocket.create_connection("ws://localhost:8000/ws?token=TEST_TOKEN")
        ws.send(json.dumps({"type": "ping"}))
        ws.recv()
        ws.close() 