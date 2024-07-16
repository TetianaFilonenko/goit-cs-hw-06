# Python Web and WebSocket Server with MongoDB

This project demonstrates a simple Python web application that uses both HTTP and WebSocket servers to manage real-time messaging, with data stored in a MongoDB database. The application uses Docker for containerization and Docker Compose to manage multiple services.

## Features

- **HTTP Server**: Serves static files and handles form submissions.
- **WebSocket Server**: Manages real-time messaging between clients.
- **MongoDB**: Stores messages with timestamps.
- **Docker**: Containerizes the application for easy deployment.
- **Bootstrap**: Provides responsive design for the front-end.

## Requirements

- Docker
- Docker Compose

## Setup

1. Clone the repository:

```sh
git clone https://github.com/TetianaFilonenko/goit-cs-hw-06
cd goit-cs-hw-06
```

2. Build and start the Docker containers:

```sh
docker-compose up --build
```

3. Open your browser and navigate to:

```
http://localhost:3000
```

## Services

- **HTTP Server**: Runs on port `3000`.
- **Socket Server**: Runs on port `5001`.
- **MongoDB**: Runs on port `27017`.

## Usage

### Access the Application

- Open your browser and go to `http://localhost:3000` to view the home page.
- Navigate to `http://localhost:3000/message.html` to send a message.

### Sending Messages

- Fill out the form with your username and message.
- Submit the form to send your message.
- Messages will appear in real-time on all connected clients.
