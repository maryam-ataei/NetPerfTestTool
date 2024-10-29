import socket
import time
import argparse
from datetime import datetime

# Argument parsing
parser = argparse.ArgumentParser(description="iperf3-like client")
parser.add_argument('-s', '--server', type=str, required=True, help="Server IP address")
parser.add_argument('-p', '--port', type=int, default=5201, help="Server port (default 5201)")
parser.add_argument('-R', '--reverse', action='store_true', help="Enable reverse mode (server sends data to client)")
parser.add_argument('--iterations', type=int, default=1, help="Number of iterations for data transfer in normal mode")
parser.add_argument('--sleep', type=int, default=0, help="Sleep duration in seconds between iterations")
parser.add_argument('--constant_rate', action='store_true', help="Enable constant rate phase after normal transfer")
parser.add_argument('--phase_time', type=int, default=5, help="Duration of constant rate phase in seconds")
parser.add_argument('--target_rate', type=int, default=None, help="Target rate in Mbps for increasing phase")
parser.add_argument('--rate_based_phase', action='store_true', help="Increase data transfer based on reaching target rate")
parser.add_argument('--time_based_phase', type=int, help="Increase data transfer for a specific time (in seconds)")
parser.add_argument('--bytes', type=int, default=None, help="Transfer a specific amount of data in bytes in normal mode")
parser.add_argument('--time', type=int, default=None, help="Duration of data transfer in seconds in normal mode")
parser.add_argument('--buffer_size', type=int, default=128 * 1024, help="Buffer size for data transfer (default 128 KB)")
args = parser.parse_args()

SERVER_IP = args.server
SERVER_PORT = args.port
BUFFER_SIZE = args.buffer_size
DATA = b'X' * BUFFER_SIZE  # Data to be sent

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

    # Send mode to the server ('N' for Normal, 'R' for Reverse)
    mode = 'R' if args.reverse else 'N'
    client_socket.sendall(mode.encode())

    if args.reverse:  # Reverse Mode: Receive data from the server
        print("Reverse Mode: Receiving data from the server.")
        total_data_received = 0
        start_time = time.time()

        try:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                total_data_received += len(data)

        except (BrokenPipeError, ConnectionResetError):
            print("Server disconnected unexpectedly.")

        elapsed_time = time.time() - start_time
        throughput_mbps = (total_data_received * 8 / (1024 * 1024)) / elapsed_time
        print(f"Total data received: {total_data_received / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")

    else:  # Normal Mode: Send data to the server
        print("Normal Mode: Sending data to the server.")

        max_throughput_mbps = 0  # To store max throughput during increasing phase

        for i in range(args.iterations):
            total_data_sent = 0
            start_time = time.time()

            print(f"[Client] Iteration {i+1} started at {datetime.now()}")

            if args.constant_rate:
                # Phase 1: Increasing Phase
                if args.rate_based_phase and args.target_rate:
                    print("[Client] Increasing phase based on target rate.")
                    # Increase transfer until target rate is reached
                    while max_throughput_mbps < args.target_rate:
                        client_socket.sendall(DATA)
                        total_data_sent += len(DATA)
                        elapsed_time = time.time() - start_time
                        max_throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time

                elif args.time_based_phase:
                    print("[Client] Increasing phase based on time.")
                    # Increase transfer for the specified time
                    phase_end_time = start_time + args.time_based_phase
                    while time.time() < phase_end_time:
                        client_socket.sendall(DATA)
                        total_data_sent += len(DATA)

                # Phase 2: Constant Rate Phase
                constant_phase_end = time.time() + args.phase_time
                bytes_per_second = max_throughput_mbps * 1024 * 1024 / 8

                print(f"[Client] Constant rate phase started at {datetime.now()}")
                while time.time() < constant_phase_end:
                    chunk_size = min(BUFFER_SIZE, int(bytes_per_second))
                    client_socket.sendall(DATA[:chunk_size])
                    total_data_sent += chunk_size

            else:
                # Non-constant rate, either bytes or time-based transfer
                if args.bytes:
                    print(f"[Client] Sending {args.bytes} bytes.")
                    bytes_to_send = args.bytes
                    while bytes_to_send > 0:
                        chunk_size = min(BUFFER_SIZE, bytes_to_send)
                        client_socket.sendall(DATA[:chunk_size])
                        total_data_sent += chunk_size
                        bytes_to_send -= chunk_size

                elif args.time:
                    print(f"[Client] Sending data for {args.time} seconds.")
                    phase_end_time = time.time() + args.time
                    while time.time() < phase_end_time:
                        client_socket.sendall(DATA)
                        total_data_sent += len(DATA)

            # Log transfer progress
            elapsed_time = time.time() - start_time
            throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
            print(f"[Client] Iteration {i+1} completed, Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")

            # Sleep between iterations if iteration mode is enabled
            if args.sleep:
                print(f"[Client] Iteration {i+1}: Sleeping for {args.sleep} seconds.")
                time.sleep(args.sleep)

finally:
    # Close the client socket
    client_socket.close()
    print("Connection closed.")
