import asyncio
import logging
import websockets
import json
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from datetime import datetime
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

client = MongoClient("mongodb://mongo:27017/")
db = client["message_database"]
collection = db["messages"]

class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

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
                await self.send_to_clients(f"{data['username']}: {data['message']}")
                self.save_message(data['username'], data['message'])
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
            except Exception as e:
                logging.error(f"Error processing message: {e}")

    def save_message(self, username, message):
        message_data = {
            "date": str(datetime.now()),
            "username": username,
            "message": message
        }
        logging.info(f"Saving message to MongoDB: {message_data}")
        try:
            result = collection.insert_one(message_data)
            logging.info(f"Message saved successfully with id {result.inserted_id}")
        except Exception as e:
            logging.error(f"Error saving message to MongoDB: {e}")

async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, '0.0.0.0', 5001):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
