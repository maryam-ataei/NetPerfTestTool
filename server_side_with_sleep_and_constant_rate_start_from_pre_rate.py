import socket
import time
import argparse
from datetime import datetime

# Argument parsing to allow changing the port, iterations, and constant rate
parser = argparse.ArgumentParser(description="iperf3-like server with previous constant rate carry-over")
parser.add_argument('-p', '--port', type=int, default=5201, help="Server port (default 5201)")
parser.add_argument('--iterations', type=int, default=1, help="Number of iterations for data transfer in reverse mode")
parser.add_argument('--sleep', type=int, default=0, help="Sleep duration in seconds between iterations")
parser.add_argument('--normal_duration', type=int, default=5, help="Duration of normal (increasing) phase in seconds")
parser.add_argument('--constant_rate', action='store_true', help="Enable constant rate phase after normal transfer")
args = parser.parse_args()

SERVER_HOST = '0.0.0.0'
SERVER_PORT = args.port
BUFFER_SIZE = 128 * 1024  # 128 KB buffer size
DATA = b'X' * BUFFER_SIZE  # The data to be sent

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print(f'Server is listening on {SERVER_HOST}:{SERVER_PORT}')

# Accept client connection
client_socket, client_address = server_socket.accept()
print(f'Client {client_address} connected.')

# Receive mode instruction from the client
mode = client_socket.recv(1).decode()

if mode == 'N':  # Normal mode: client sends data to server
    total_data_received = 0
    print("Normal mode: client is sending data to server.")
    
    try:
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            total_data_received += len(data)

    except (BrokenPipeError, ConnectionResetError):
        print("Client disconnected.")
    finally:
        print(f"Total data received: {total_data_received / (1024 * 1024):.2f} MB")
        client_socket.close()

else:  # Reverse mode: server sends data to client
    print("Reverse mode: server is sending data to client.")

    # Initialize starting throughput for the increasing phase
    start_throughput_mbps = 1  # Start from 1 Mbps initially

    for i in range(args.iterations):
        total_data_sent = 0
        start_time = time.time()

        print(f"[Server] Iteration {i+1} started at {datetime.now()}")

        # Phase 1: Increasing phase starts from the last constant rate
        current_rate_mbps = start_throughput_mbps
        increasing_phase_end = time.time() + args.normal_duration

        while time.time() < increasing_phase_end:
            bytes_per_second = current_rate_mbps * 1024 * 1024 / 8
            chunk_size = min(BUFFER_SIZE, int(bytes_per_second))
            client_socket.sendall(DATA[:chunk_size])
            total_data_sent += chunk_size
            
            elapsed_time = time.time() - start_time
            current_rate_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time  # Calculate current throughput

        print(f"[Server] Iteration {i+1}, Increasing Phase: Reached {current_rate_mbps:.2f} Mbps, Data sent: {total_data_sent / (1024 * 1024):.2f} MB")

        # Phase 2: Constant rate phase
        if args.constant_rate:
            print(f"[Server] Iteration {i+1}, Constant Rate Phase: Maintaining {current_rate_mbps:.2f} Mbps")
            constant_phase_end = time.time() + args.normal_duration
            bytes_per_second = current_rate_mbps * 1024 * 1024 / 8

            while time.time() < constant_phase_end:
                chunk_size = min(BUFFER_SIZE, int(bytes_per_second))
                client_socket.sendall(DATA[:chunk_size])
                total_data_sent += chunk_size
                time.sleep(1)

            # Update the starting throughput for the next iteration
            start_throughput_mbps = current_rate_mbps

        # Log transfer progress
        elapsed_time = time.time() - start_time
        throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
        print(f"[Server] Iteration {i+1}, Total Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")

        # Sleep between iterations if specified
        if args.sleep:
            print(f"[Server] Iteration {i+1}: Sleeping for {args.sleep} seconds at {datetime.now()}")
            time.sleep(args.sleep)

# Close the server socket
server_socket.close()

