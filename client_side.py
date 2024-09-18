import socket
import time
import argparse

# Argument parsing to support reverse mode and port selection
parser = argparse.ArgumentParser(description="Simple iperf3-like client with reverse mode and logging")
parser.add_argument('-s', '--server', type=str, required=True, help="Server IP address")
parser.add_argument('-p', '--port', type=int, default=5201, help="Server port (default 5201)")
parser.add_argument('-t', '--time', type=int, default=10, help="Duration of data transfer in seconds")
parser.add_argument('-R', '--reverse', action='store_true', help="Enable reverse mode (server sends data to client)")

args = parser.parse_args()

SERVER_HOST = args.server
SERVER_PORT = args.port
BUFFER_SIZE = 128 * 1024  # 128 KB buffer size
DATA = b'X' * BUFFER_SIZE  # Data to be sent in normal mode
DOWNLOAD_DURATION = args.time
LOG_INTERVAL = 1  # Log every 1 second

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((SERVER_HOST, SERVER_PORT))
print(f'Connected to server at {SERVER_HOST}:{SERVER_PORT}')

# If reverse mode is enabled, send 'R' to the server; otherwise, send 'N'
if args.reverse:
    client_socket.sendall(b'R')
    print("Reverse mode: server will send data to client.")
    
    start_time = time.time()
    total_data_received = 0
    log_time = start_time
    
    try:
        # Receive data for the specified duration
        while time.time() - start_time < DOWNLOAD_DURATION:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            total_data_received += len(data)
            
            # Log transfer progress
            if time.time() - log_time >= LOG_INTERVAL:
                elapsed_time = time.time() - start_time
                throughput_mbps = (total_data_received * 8 / (1024 * 1024)) / elapsed_time
                print(f"[Client] Time: {elapsed_time:.2f}s, Data received: {total_data_received / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")
                log_time = time.time()

    except KeyboardInterrupt:
        print("Download interrupted.")
    finally:
        client_socket.close()
    
    # Report the total data received
    print(f'Total data received: {total_data_received / (1024 * 1024):.2f} MB')

else:
    client_socket.sendall(b'N')
    print("Normal mode: client will send data to server.")
    
    start_time = time.time()
    total_data_sent = 0
    log_time = start_time
    
    try:
        # Send data for the specified duration
        while time.time() - start_time < DOWNLOAD_DURATION:
            client_socket.sendall(DATA)
            total_data_sent += len(DATA)
            
            # Log transfer progress
            if time.time() - log_time >= LOG_INTERVAL:
                elapsed_time = time.time() - start_time
                throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
                print(f"[Client] Time: {elapsed_time:.2f}s, Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")
                log_time = time.time()

    except KeyboardInterrupt:
        print("Data transfer interrupted.")
    finally:
        client_socket.close()
    
    # Report the total data sent
    print(f"Total data sent: {total_data_sent / (1024 * 1024):.2f} MB")