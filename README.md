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


## New Feature
It includes additional features for data transfer iterations, sleep intervals, and byte-specific transfers.

- **Iteration Support:** Allows running multiple iterations of data transfer, with optional sleep intervals between each iteration.
- **Sleep Interval:** Specify sleep duration between data transfer iterations to simulate varying network conditions.
- **Byte-Specific Transfer:** Option to transfer a specific amount of data (in bytes) during each iteration.

### Usage
#### Server
Start the server on the machine where you want to run the bandwidth test:

bash
python server_side_with_new_feature.py [-p PORT] [--iterations ITERATIONS] [--sleep SLEEP] [--bytes BYTES] [--time TIME]

`-p PORT`: Optional. The port to listen on (default is 5201).
`--iterations ITERATIONS`: Optional. Number of iterations for reverse mode.
`--sleep SLEEP`: Optional. Sleep duration in seconds between iterations in reverse mode.
`--bytes BYTES`: Optional. Transfer a specific amount of data (in bytes) in reverse mode.
`--time TIME`: Optional. Duration of data transfer (in seconds) in reverse mode.

#### Client
Start the client on the machine where you want to initiate the test:

bash
python client_side_with_new_feature.py -s SERVER_IP [-p PORT] [-t TIME] [-R] [--iterations ITERATIONS] [--sleep SLEEP] [--bytes BYTES]

`-s SERVER_IP`: Required. The IP address of the server.
`-p PORT`: Optional. The port of the server (default is 5201).
`-t TIME`: Optional. The duration of the test in seconds (default is 10 seconds).
`-R`: Optional. Enables reverse mode where the server sends data to the client.
`--iterations ITERATIONS`: Optional. Number of iterations for data transfer.
`--sleep SLEEP`: Optional. Sleep duration in seconds between iterations.
`--bytes BYTES`: Optional. Transfer a specific amount of data (in bytes) per iteration.

##### Examples
Normal mode with 10-second data transfer:

bash
python client.py -s 192.168.1.1 -t 10
Reverse mode with 5 iterations, each transferring 200 MB and sleeping for 5 seconds:

bash
python client.py -s 192.168.1.1 -R --iterations 5 --bytes 209715200 --sleep 5
Server with a port change and 3 iterations in reverse mode:

bash
Copy code
python server.py -p 5202 --iterations 3

