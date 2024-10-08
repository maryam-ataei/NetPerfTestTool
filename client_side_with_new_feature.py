import socket
import time
import argparse

# Argument parsing to support reverse mode, port selection, and new features
parser = argparse.ArgumentParser(description="Simple iperf3-like client with reverse mode and logging")
parser.add_argument('-s', '--server', type=str, required=True, help="Server IP address")
parser.add_argument('-p', '--port', type=int, default=5201, help="Server port (default 5201)")
parser.add_argument('-t', '--time', type=int, default=None, help="Duration of data transfer in seconds")
parser.add_argument('-R', '--reverse', action='store_true', help="Enable reverse mode (server sends data to client)")
parser.add_argument('--iterations', type=int, default=None, help="Number of iterations for data transfer (optional)")
parser.add_argument('--sleep', type=int, default=None, help="Sleep duration in seconds between iterations (optional)")
parser.add_argument('--bytes', type=int, default=None, help="Transfer a specific amount of data in bytes (optional)")

args = parser.parse_args()

SERVER_HOST = args.server
SERVER_PORT = args.port
BUFFER_SIZE = 128 * 1024  # 128 KB buffer size
DATA = b'X' * BUFFER_SIZE  # Data to be sent in normal mode
LOG_INTERVAL = 1  # Log every 1 second

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((SERVER_HOST, SERVER_PORT))
print(f'Connected to server at {SERVER_HOST}:{SERVER_PORT}')

if args.reverse:
    # Reverse mode: server sends data to the client
    client_socket.sendall(b'R')
    print("Reverse mode: server will send data to client.")
    
    total_data_received = 0
    for i in range(args.iterations or 1):  # Handle iterations if specified, otherwise continuous
        start_time = time.time()
        log_time = start_time

        try:
            while (args.iterations and (time.time() - start_time < args.time)) or (not args.iterations and (args.time is None or time.time() - start_time < args.time)):
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                total_data_received += len(data)

                # Log transfer progress
                if time.time() - log_time >= LOG_INTERVAL:
                    elapsed_time = time.time() - start_time
                    throughput_mbps = (total_data_received * 8 / (1024 * 1024)) / elapsed_time
                    print(f"[Client] Iteration {i+1}, Time: {elapsed_time:.2f}s, Data received: {total_data_received / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")
                    log_time = time.time()

            # Sleep between iterations if iteration mode is enabled
            if args.iterations and args.sleep:
                print(f"Sleeping for {args.sleep} seconds...")
                time.sleep(args.sleep)

        except KeyboardInterrupt:
            print("Download interrupted.")
            break

else:
    # Normal mode: client sends data to the server
    client_socket.sendall(b'N')
    print("Normal mode: client will send data to server.")
    
    for i in range(args.iterations or 1):  # Handle iterations if specified, otherwise continuous
        total_data_sent = 0
        start_time = time.time()
        
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
                while (args.iterations and time.time() - start_time < args.time) or (not args.iterations and (args.time is None or time.time() - start_time < args.time)):
                    client_socket.sendall(DATA)
                    total_data_sent += len(DATA)

            # Log transfer progress
            elapsed_time = time.time() - start_time
            throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
            print(f"[Client] Iteration {i+1}, Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")

            # Sleep between iterations if iteration mode is enabled
            if args.iterations and args.sleep:
                print(f"Sleeping for {args.sleep} seconds...")
                time.sleep(args.sleep)

        except KeyboardInterrupt:
            print("Data transfer interrupted.")
            break

# Close the socket
client_socket.close()
print(f"Completed {args.iterations or 1} iterations.")
