import http.server
import socketserver
import os
import json
import socket
import asyncio
import logging
import websockets
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from pymongo import MongoClient
from multiprocessing import Process
from urllib.parse import parse_qs

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

client = MongoClient("mongodb://mongo:27017/")
db = client["message_database"]
collection = db["messages"]


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "index.html"
        elif self.path == "/message.html":
            self.path = "message.html"
        elif self.path == "/style.css":
            self.path = "style.css"
        elif self.path == "/script.js":
            self.path = "script.js"
        elif self.path == "/logo.png":
            self.path = "logo.png"
        else:
            self.path = "error.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            post_data = parse_qs(post_data.decode("utf-8"))
            message_data = {
                "username": post_data["username"][0],
                "message": post_data["message"][0],
            }

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", 5001))
            sock.sendall(json.dumps(message_data).encode("utf-8"))
            sock.close()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Message sent"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Page not found")


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        self.clients.add(ws)
        logging.info(f"{ws.remote_address} connects")

        previous_messages = collection.find().sort("date")
        for message in previous_messages:
            await ws.send(
                json.dumps(
                    {
                        "username": message["username"],
                        "message": message["message"],
                        "date": message["date"],
                    }
                )
            )

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f"{ws.remote_address} disconnects")

    async def send_to_clients(self, message: str):
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            try:
                logging.info(f"Message received: {message}")
                data = json.loads(message)
                await self.send_to_clients(
                    json.dumps(
                        {
                            "username": data["username"],
                            "message": data["message"],
                            "date": data["date"],
                        }
                    )
                )
                self.save_message(data["username"], data["message"], data["date"])
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
            except Exception as e:
                logging.error(f"Error processing message: {e}")

    def save_message(self, username, message, date):
        message_data = {
            "date": date,
            "username": username,
            "message": message,
        }
        logging.info(f"Saving message to MongoDB: {message_data}")
        try:
            result = collection.insert_one(message_data)
            logging.info(f"Message saved successfully with id {result.inserted_id}")
        except Exception as e:
            logging.error(f"Error saving message to MongoDB: {e}")


def start_http_server():
    PORT = 3000
    os.chdir("static")
    httpd = socketserver.TCPServer(("", PORT), Handler)
    logging.info(f"Serving on port {PORT}")
    httpd.serve_forever()


async def start_websocket_server():
    server = Server()
    async with websockets.serve(server.ws_handler, "0.0.0.0", 5001):
        await asyncio.Future()


def start_websocket_process():
    asyncio.run(start_websocket_server())


if __name__ == "__main__":
    p1 = Process(target=start_http_server)
    p2 = Process(target=start_websocket_process)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
