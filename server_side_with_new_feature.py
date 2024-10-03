import socket
import time
import argparse

# Argument parsing to allow changing the port
parser = argparse.ArgumentParser(description="iperf3-like server")
parser.add_argument('-p', '--port', type=int, default=5201, help="Server port (default 5201)")
args = parser.parse_args()

# Server configuration
SERVER_HOST = '0.0.0.0'
SERVER_PORT = args.port
BUFFER_SIZE = 128 * 1024  # 128 KB buffer size
DATA = b'X' * BUFFER_SIZE  # The data to be sent
LOG_INTERVAL = 1  # Log every 1 second

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
    start_time = time.time()
    log_time = start_time
    print("Normal mode: client is sending data to server.")
    
    try:
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            total_data_received += len(data)
            
            # Log transfer progress
            if time.time() - log_time >= LOG_INTERVAL:
                elapsed_time = time.time() - start_time
                throughput_mbps = (total_data_received * 8 / (1024 * 1024)) / elapsed_time
                print(f"[Server] Time: {elapsed_time:.2f}s, Data received: {total_data_received / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")
                log_time = time.time()

    except (BrokenPipeError, ConnectionResetError):
        print("Client disconnected.")
    finally:
        print(f"Total data received from client: {total_data_received / (1024 * 1024):.2f} MB")
        client_socket.close()

else:  # Reverse mode: server sends data to client
    total_data_sent = 0
    start_time = time.time()
    log_time = start_time
    print("Reverse mode: server is sending data to client.")
    
    # Optionally support iterations and sleep (handled by the client-side logic)
    # For reverse mode, we assume the client handles iterations and sleep requests
    try:
        while True:
            client_socket.sendall(DATA)
            total_data_sent += len(DATA)
            
            # Log transfer progress
            if time.time() - log_time >= LOG_INTERVAL:
                elapsed_time = time.time() - start_time
                throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
                print(f"[Server] Time: {elapsed_time:.2f}s, Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")
                log_time = time.time()

    except (BrokenPipeError, ConnectionResetError):
        print("Client disconnected.")
    finally:
        client_socket.close()

# Close the server socket
server_socket.close()
