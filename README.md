# Simple_Network_Performance_Tool

This tool allows you to test bandwidth between a client and server by sending data between them. It supports both normal and reverse modes, where the client can send data to the server or the server can send data to the client.

## Features

- **Client-Server Architecture**: Test network performance between two machines.
- **Normal Mode**: Client sends data to the server.
- **Reverse Mode**: Server sends data to the client.
- **Customizable Port**: Specify the port to be used for communication (default is 5201).
- **Real-Time Logging**: Logs data transfer progress every second, including data sent/received and throughput in Mbps.
- **TCP Socket**: Data is transferred over a TCP connection.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/maryam-ataei/NetPerfTestTool.git
   cd NetPerfTestTool
   
2. Ensure Python 3.x is installed on both the client and server machines.

## Usage

### Server
Start the server on the machine where you want to run the bandwidth test:
   ```bash
python server.py [-p PORT]
```
`-p PORT`: Optional. The port to listen on (default is 5201).

### Client
Start the client on the machine where you want to initiate the test:
   ```bash
python client.py -s SERVER_IP [-p PORT] [-t TIME] [-R]
```

`-s SERVER_IP`: Required. The IP address of the server.

`-p PORT`: Optional. The port of the server (default is 5201).

`-t TIME`: Optional. The duration of the test in seconds (default is 10 seconds).

`-R`: Optional. Enables reverse mode where the server sends data to the client.



