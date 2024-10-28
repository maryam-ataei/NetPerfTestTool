import socket
import time
import argparse
from datetime import datetime

# Argument parsing to allow changing the port and handling iterations and sleep for reverse mode
parser = argparse.ArgumentParser(description="iperf3-like server")
parser.add_argument('-p', '--port', type=int, default=5201, help="Server port (default 5201)")
parser.add_argument('--iterations', type=int, default=1, help="Number of iterations for data transfer in reverse mode")
parser.add_argument('--sleep', type=int, default=0, help="Sleep duration in seconds between iterations in reverse mode")
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

else:  # Reverse mode: server sends data to client (server controls iteration and sleep)
    print("Reverse mode: server is sending data to client.")
    
    for i in range(args.iterations or 1):  # Handle iterations if specified
        total_data_sent = 0
        start_time = time.time()

        print(f"[Server] Iteration {i+1} started at {datetime.now()}")
        
        try:
            if args.bytes:
                # Transfer a specific amount of bytes
                bytes_to_send = args.bytes
                while bytes_to_send > 0:
                    chunk_size = min(BUFFER_SIZE, bytes_to_send)
                    client_socket.sendall(DATA[:chunk_size])
                    total_data_sent += chunk_size
                    bytes_to_send -= chunk_size
            else:
                # Transfer for a specified time
                while time.time() - start_time < args.time:
                    client_socket.sendall(DATA)
                    total_data_sent += len(DATA)

            # Log transfer progress
            elapsed_time = time.time() - start_time
            throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
            print(f"[Server] Iteration {i+1} completed at {datetime.now()}, Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")

            # Sleep between iterations if iteration mode is enabled
            if args.sleep:
                print(f"[Server] Iteration {i+1}: Sleeping for {args.sleep} seconds at {datetime.now()}")
                time.sleep(args.sleep)

        except (BrokenPipeError, ConnectionResetError):
            print("Client disconnected.")
            break

# Close the server socket
server_socket.close()
