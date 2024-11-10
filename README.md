# Server-Client Communication System

This project implements a robust server-client communication system using Python, featuring a multi-threaded server setup capable of managing multiple client connections, logging requests, handling client inactivity, and supporting a controlled shutdown process. Below is a thorough breakdown of each script, its purpose, setup instructions, and usage tips.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [File Descriptions](#file-descriptions)
   - [`server.py`](#serverpy)
   - [`client.py`](#clientpy)
   - [`shutdown.py`](#shutdownpy)
   - [`server_logs.txt`](#server_logstxt)
3. [System Requirements](#system-requirements)
4. [Setup and Execution](#setup-and-execution)
5. [Usage and Interaction](#usage-and-interaction)
6. [Troubleshooting and Common Issues](#troubleshooting-and-common-issues)

---

## Project Overview

The system is designed to facilitate a connection-oriented communication protocol between a server and multiple clients. This allows users to connect clients to the server, exchange messages, monitor server activities, and implement a clean shutdown without data loss or abrupt disconnections.

## File Descriptions

### `server.py`
This script is the backbone of the project, setting up a multi-threaded server that listens for and manages client connections. Here’s a detailed breakdown of its functionalities:

1. **Network Configuration**:
   - IP Address: `0.0.0.0` (binds to all available interfaces).
   - Port: `12345` (default listening port for client connections).
   - Max Connections: Set to 5 to limit the number of simultaneous clients.

2. **Client Management**:
   - Each client is managed using threads to allow concurrent handling.
   - `client_lock`: A threading lock to prevent race conditions when accessing the shared `clients` list.

3. **Logging**:
   - Each request and server response is logged to `server_logs.txt`, recording timestamp, client IP, and the message.
   - The `log_request()` function writes these entries, aiding in debugging and tracking server activity.

4. **Timeout Handling**:
   - **Inactivity Timeout**: If a client remains inactive for over 2 minutes, the server disconnects it.
   - **Response Timeout**: The server waits up to 12 seconds for a client response before considering the client inactive.

5. **Access Control**:
   - The server only grants full access to specific IP addresses listed in `FULL_ACCESS_CLIENTS`, adding a layer of security.

6. **Multithreading**:
   - The server uses Python’s threading to allow multiple clients to connect simultaneously. Each client’s interaction runs in its own thread to ensure efficient and independent communication.

**Detailed Flow**:
   - Upon starting, the server binds to the specified IP and port and begins listening for incoming connections.
   - When a client connects, a new thread is created for that client, which continuously listens for messages.
   - If a client remains inactive for too long, the thread managing that client disconnects it and logs the event.

### `client.py`
The client script is designed for users to connect to the server and exchange messages. Key features include:

1. **Connection Setup**:
   - Attempts to connect to the server on the specified IP and port.
   - Once connected, it enters a loop where it listens for messages from the server.

2. **Message Reception**:
   - The `receive_messages()` function handles incoming messages and displays them, ensuring real-time updates.

3. **Error Handling**:
   - The script catches and displays connection errors, disconnections, and timeouts, ensuring the client is informed of any connection issues.

**Detailed Flow**:
   - On execution, the client connects to the server and awaits messages.
   - If the connection is lost or an error occurs, the client displays a message and exits, allowing the user to attempt reconnection.

### `shutdown.py`
A standalone script for gracefully shutting down the server:

1. **Shutdown Execution**:
   - When run, it prints a shutdown message to the console.
   - Calls `sys.exit(0)` to close the script. This can be expanded to perform additional cleanups, like stopping other services or saving logs.

### `server_logs.txt`
A log file that records server events, including connection requests, disconnections, message exchanges, and error logs.

- Logs are timestamped for easy tracking.
- Useful for debugging, performance monitoring, and auditing.

## System Requirements

- **Python**: Version 3.x
- **Libraries**: Only standard libraries are used (`socket`, `threading`, `time`, `datetime`, `sys`, and `subprocess`), so no additional packages are required.

## Setup and Execution

1. **Start the Server**:
   - Open a terminal and navigate to the project directory.
   - Run the server script:
     ```bash
     python server.py
     ```

2. **Connect Clients**:
   - Open multiple terminals (or instances of the command prompt) and run the client script to simulate multiple clients:
     ```bash
     python client.py
     ```

3. **Shut Down the Server**:
   - To gracefully stop the server, open a new terminal and run:
     ```bash
     python shutdown.py
     ```

## Usage and Interaction

- **Sending Messages**: Once connected, clients can send messages to the server by typing into their terminals. The server will log each message and may respond based on the programmed logic.
- **Inactivity Handling**: If a client remains idle for over 2 minutes, it will be disconnected.
- **Server Logs**: Check `server_logs.txt` to view activity logs and monitor server health and client interactions.

## Troubleshooting and Common Issues

- **Connection Refused**: Ensure the server is running and listening on the specified IP and port.
- **Client Disconnection**: This may happen if the client is inactive for over 2 minutes or if there are network issues.
- **IP Access Denied**: If you’re connecting from an IP not in `FULL_ACCESS_CLIENTS`, the server will reject the connection. Update the IP list in `server.py` to allow new clients.