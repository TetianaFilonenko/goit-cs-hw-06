# Python WebSocket and HTTP Server Application

This project is a simple web application that includes an HTTP server and a WebSocket server. The HTTP server serves static files, while the WebSocket server handles real-time messaging and stores messages in MongoDB.

## Features

- Serve static files (HTML, CSS, JS)
- Real-time messaging via WebSocket
- Store messages in MongoDB
- Display previous messages upon connection

## Requirements

- Docker
- Docker Compose

## Setup

1. Clone the repository:

```sh
git clone https://github.com/TetianaFilonenko/goit-cs-hw-06
cd goit-cs-hw-06
```

2. Build and start the services:

```sh
docker-compose up --build
```

3. Open your browser and navigate to:

```
http://localhost:3000
```
