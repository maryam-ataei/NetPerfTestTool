import socket
import time
import argparse
from datetime import datetime

# Argument parsing
parser = argparse.ArgumentParser(description="iperf3-like server with previous constant rate carry-over")
parser.add_argument('-p', '--port', type=int, default=5201, help="Server port (default 5201)")
parser.add_argument('-iter', '--iterations', type=int, default=1, help="Number of iterations for data transfer in reverse mode")
parser.add_argument('--sleep', type=int, default=0, help="Sleep duration in seconds between iterations")
parser.add_argument('--constant_rate', action='store_true', help="Enable constant rate phase after normal transfer")
parser.add_argument('--consphase_time', type=int, default=5, help="Duration of constant rate phase in seconds")
parser.add_argument('--target_rate', type=int, default=None, help="Target rate in Mbps for increasing phase")
parser.add_argument('--rate_based_phase', action='store_true', help="Increase data transfer based on reaching target rate")
parser.add_argument('--time_based_phase', type=int, help="Increase data transfer for a specific time (in seconds)")
parser.add_argument('--bytes', type=int, default=None, help="Transfer a specific amount of data in bytes in reverse mode")
parser.add_argument('--time', type=int, default=None, help="Duration of data transfer in seconds in reverse mode")

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

if mode not in ['N', 'R']:
    print("Invalid mode received.")
    client_socket.close()
    server_socket.close()
    exit(1)

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

    for i in range(args.iterations):
        total_data_sent = 0  # Reset total data sent for each iteration
        avg_throughput_mbps = 0  # Reset avg throughput

        print(f"[Server] Iteration {i+1} started at {datetime.now()}")

        start_time = time.time()

        if args.constant_rate:
            # Phase 1: Increasing Phase
            if args.rate_based_phase and args.target_rate:
                print("[Server] Increasing phase based on target rate.")

                # Set target rate for the current iteration
                if i == 0:
                    current_target_rate = args.target_rate
                else:
                    current_target_rate = args.target_rate * (1 + 0.2 * i)  # Increase by 20% per iteration

                current_byte_send = current_target_rate * (1024 * 1024) / 8

                # Increase transfer until target rate is reached
                while total_data_sent < current_byte_send:
                    remaining_bytes = current_byte_send - total_data_sent
                    chunk_size = min(len(DATA), int(remaining_bytes))

                    if chunk_size <= 0:
                        break

                    client_socket.sendall(DATA[:chunk_size])
                    total_data_sent += chunk_size

            elif args.time_based_phase:
                print("[Server] Increasing phase based on time.")

                increasing_phase_end = time.time() + args.time_based_phase

                while time.time() < increasing_phase_end:
                    client_socket.sendall(DATA)
                    total_data_sent += len(DATA)
                    elapsed_time = time.time() - start_time
                    throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time

                current_byte_send = total_data_sent


            print(f"[Server] Increasing phase ended, total_data_sent = {total_data_sent / (1024 * 1024):.2f} MB")

            # Phase 2: Constant Rate Phase
            constant_phase_end = time.time() + args.consphase_time

            # Target bytes for the constant phase
            bytes_in_constant_rate = current_byte_send  # Target bytes from the increasing phase
            bytes_per_second = bytes_in_constant_rate / args.consphase_time  # Calculate bytes per second

            print(f"[Server] Constant rate phase started at {datetime.now()} with target bytes {bytes_in_constant_rate:.2f} B")

            interval = 0.01  # Interval in seconds (10 ms)
            bytes_per_interval = bytes_per_second * interval  # Bytes to send per interval

            # Track start time for pacing
            start_time = time.time()

            # Reset constant phase-specific data sent
            constant_phase_data_sent = 0

            while time.time() < constant_phase_end:
                # Calculate remaining bytes to send in this interval
                remaining_bytes = bytes_in_constant_rate - constant_phase_data_sent
                if remaining_bytes <= 0:
                    print("remaining_bytes is less than zero")
                    break

                # Calculate how many bytes to send in this interval
                chunk_size = min(int(bytes_per_interval), len(DATA))
                chunk_size = min(chunk_size, int(remaining_bytes))  # Adjust chunk size

                # Send the chunk
                client_socket.sendall(DATA[:chunk_size])
                constant_phase_data_sent += chunk_size

                # Calculate elapsed time and sleep for pacing
                elapsed_time = time.time() - start_time
                sleep_time = interval - (elapsed_time % interval)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            total_data_sent += constant_phase_data_sent  # Update total data sent
            print(f"[Server] Constant rate ended: total_data_sent = {total_data_sent / (1024 * 1024):.2f} MB, time = {datetime.now()}.")

        else:
            # Non-constant rate, either bytes or time-based transfer
            if args.bytes:
                print(f"[Server] Sending {args.bytes} bytes.")
                bytes_to_send = args.bytes
                while bytes_to_send > 0:
                    chunk_size = min(BUFFER_SIZE, bytes_to_send)
                    client_socket.sendall(DATA[:chunk_size])
                    total_data_sent += chunk_size
                    bytes_to_send -= chunk_size

            elif args.time:
                print(f"[Server] Sending data for {args.time} seconds.")
                phase_end_time = time.time() + args.time
                while time.time() < phase_end_time:
                    client_socket.sendall(DATA)
                    total_data_sent += len(DATA)

        # Log transfer progress
        elapsed_time = time.time() - start_time
        throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
        print(f"[Server] Iteration {i+1} completed, Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")

        # Sleep between iterations if iteration mode is enabled
        if args.sleep:
            print(f"[Server] Iteration {i+1}: Sleeping for {args.sleep} seconds.")
            time.sleep(args.sleep)

# Close the server socket
server_socket.close()
