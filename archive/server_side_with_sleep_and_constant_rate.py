import socket
import time
import argparse
from datetime import datetime

# Argument parsing to allow changing the port and handling iterations, sleep, and constant rate for reverse mode
parser = argparse.ArgumentParser(description="iperf3-like server")
parser.add_argument('-p', '--port', type=int, default=5201, help="Server port (default 5201)")
parser.add_argument('--iterations', type=int, default=1, help="Number of iterations for data transfer in reverse mode")
parser.add_argument('--sleep', type=int, default=0, help="Sleep duration in seconds between iterations in reverse mode")
parser.add_argument('--bytes', type=int, default=None, help="Transfer a specific amount of data in bytes in reverse mode")
parser.add_argument('--time', type=int, default=None, help="Duration of data transfer in seconds in reverse mode")
parser.add_argument('--constant_rate', action='store_true', help="Enable constant rate mode after normal transfer (optional)")
parser.add_argument('--normal_duration', type=int, default=5, help="Duration of normal data transfer before switching to constant rate (seconds)")
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

else:  # Reverse mode: server sends data to client (server controls iteration and constant rate)
    print("Reverse mode: server is sending data to client.")
    
    for i in range(args.iterations or 1):  # Handle iterations if specified
        total_data_sent = 0
        start_time = time.time()
        max_throughput_mbps = 0  # To store max throughput during increasing phase

        print(f"[Server] Iteration {i+1} started at {datetime.now()}")
        
        try:
            # Phase 1: Increasing data transfer for 'normal_duration'
            increasing_phase_end = start_time + args.normal_duration
            while time.time() < increasing_phase_end:
                client_socket.sendall(DATA)
                total_data_sent += len(DATA)
                elapsed_time = time.time() - start_time
                throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
                max_throughput_mbps = max(max_throughput_mbps, throughput_mbps)

            print(f"[Server] Iteration {i+1}, Increasing Phase: Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Max Throughput: {max_throughput_mbps:.2f} Mbps")
            
            # Phase 2: Constant rate transfer
            if args.constant_rate:
                print(f"[Server] Iteration {i+1}, Constant Rate Phase: Maintaining {max_throughput_mbps:.2f} Mbps for {args.normal_duration} seconds.")
                constant_phase_end = time.time() + args.normal_duration
                bytes_per_second = max_throughput_mbps * 1024 * 1024 / 8

                while time.time() < constant_phase_end:
                    chunk_size = min(BUFFER_SIZE, int(bytes_per_second))
                    client_socket.sendall(DATA[:chunk_size])
                    total_data_sent += chunk_size
                    time.sleep(1)  # Send data in 1-second intervals

            # Log transfer progress
            elapsed_time = time.time() - start_time
            throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
            print(f"[Server] Iteration {i+1}, Total Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")

            # Sleep between iterations if iteration mode is enabled
            if args.iterations and args.sleep:
                print(f"[Server] Iteration {i+1}: Sleeping for {args.sleep} seconds at {datetime.now()}")
                time.sleep(args.sleep)

        except (BrokenPipeError, ConnectionResetError):
            print("Client disconnected.")
            break

# Close the server socket
server_socket.close()



#python3 server_script_name.py -p 5201 --iterations 2 --time 10 --normal_duration 10 --constant_rate
#Explanation:
#-p 5201: Sets the port to 5201.
#--iterations 2: Runs 2 iterations of the data transfer process.
#--time 10: Sets the duration for data transfer to 10 seconds.
#--normal_duration 10: Sets both the increasing and constant phases to 10 seconds.
#--constant_rate: Enables the constant rate phase after the increasing phase.

#python3 server_script_name.py -p 5201 --iterations 2 --time 10 --normal_duration 10 --constant_rate --sleep 5
#Explanation:
#--constant_rate: Enables constant rate transfer after the increasing phase.
#--sleep 5: Adds a 5-second sleep interval between iterations.
#The server will:
#Send data at an increasing rate for 10 seconds.
#Switch to a constant rate for another 10 seconds.
#Sleep for 5 seconds before starting the next iteration.
#Behavior:
#The server will still perform the increasing phase, followed by the constant rate phase.
#After each iteration, it will sleep for the specified number of seconds before starting the next one.
#If --constant_rate is not specified, it will skip the constant rate phase and only have the increasing phase followed by the sleep interval.
