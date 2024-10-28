# Simple_Network_Performance_Tool

This tool allows you to test bandwidth between a client and server by sending data between them. It supports both normal and reverse modes, where the client can send data to the server or the server can send data to the client.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/maryam-ataei/NetPerfTestTool.git
   cd NetPerfTestTool

2. Ensure Python 3.x is installed on both the client and server machines.

## Basic version

The basic version of the tool uses the `server_side.py` and `client_side.py` scripts, which only support simple data transfer in normal or reverse mode

### Usage

#### Server
Start the basic server on the machine where you want to run the bandwidth test:

```bash
python server.py [-p PORT]
```
`-p PORT`: Optional. The port to listen on (default is 5201).

#### Client

Start the basic client on the machine where you want to initiate the test:

```bash
python client.py -s SERVER_IP [-p PORT] [-t TIME] [-R]
```

`-s SERVER_IP`: Required. The IP address of the server.

`-p PORT`: Optional. The port of the server (default is 5201).

`-t TIME`: Optional. The duration of the test in seconds (default is 10 seconds).

`-R`: Optional. Enables reverse mode where the server sends data to the client.

## Advanced code

The advanced version of the tool supports constant rate transmission (based on reaching a target rate or based on time) and iterations (based on bytes with sleep or time with sleep).

### Features

- **Client-Server Architecture**: Test network performance between two machines.
- **Normal Mode**: Client sends data to the server.
- **Reverse Mode**: Server sends data to the client.
- **Constant Rate Transmission**: Supports constant rate transfer based on reaching a target rate or for a specific duration.
- **Iteration and sleep**: Supports sending data based on time or bytes, with sleep intervals and repetition.
- **Customizable Port**: Specify the port to be used for communication (default is 5201).
- **Real-Time Logging**: Logs data transfer progress every second, including data sent/received and throughput in Mbps.
- **TCP Socket**: Data is transferred over a TCP connection.

### Advanced Server
The advanced server supports both normal and reverse modes with additional features for constant rate transmission and iterations:

```bash
python advanced_server.py [-p PORT] [--constant_rate] [--iterations N] [--target_rate RATE] [--phase_time TIME] [--rate_based_phase] [--time_based_phase TIME]
```

`-p PORT`: Optional. The port to listen on (default is 5201).

`--constant_rate`: Optional. Enables constant rate phase after normal transfer.

`--iterations N`: Optional. Sets the number of iterations for data transfer.

`--target_rate RATE`: Optional. Sets the target rate for the increasing phase in Mbps.

`--phase_time TIME`: Optional. Sets the duration of the constant rate phase in seconds.

`--rate_based_phase`: Optional. Increases the data transfer rate until the target rate is reached, before switching to a constant rate.

`--time_based_phase TIME`: Optional. Increases the data transfer rate for a specified duration before switching to a constant rate.


### Advanced Client
The advanced client adds similar enhancements for sending data to the server:

```bash
python advanced_client.py -s SERVER_IP [-p PORT] [--constant_rate] [--iterations N] [--target_rate RATE] [--phase_time TIME] [--rate_based_phase] [--time_based_phase TIME] [-R]
```

`-s SERVER_IP`: Required. The IP address of the server.

`-p PORT`: Optional. The port of the server (default is 5201).

`--constant_rate`: Optional. Enables constant rate phase after normal transfer.

`--iterations N`: Optional. Sets the number of iterations for data transfer.

`--target_rate RATE`: Optional. Sets the target rate for the increasing phase in Mbps.

`--phase_time TIME`: Optional. Sets the duration of the constant rate phase in seconds.

`--rate_based_phase`: Optional. Increases the data transfer rate until the target rate is reached, before switching to a constant rate.

`--time_based_phase TIME`: Optional. Increases the data transfer rate for a specified duration before switching to a constant rate.

`-R`: Optional. Enables reverse mode where the server sends data to the client.


