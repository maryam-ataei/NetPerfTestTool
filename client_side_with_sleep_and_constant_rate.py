import socket
import time
import argparse

# Argument parsing to support reverse mode, port selection, and new features
parser = argparse.ArgumentParser(description="Simple iperf3-like client with reverse mode and logging by sleep between send data or constant rate")
parser.add_argument('-s', '--server', type=str, required=True, help="Server IP address")
parser.add_argument('-p', '--port', type=int, default=5201, help="Server port (default 5201)")
parser.add_argument('-t', '--time', type=int, default=10, help="Total duration of data transfer in seconds")
parser.add_argument('-R', '--reverse', action='store_true', help="Enable reverse mode (server sends data to client)")
parser.add_argument('--iterations', type=int, default=None, help="Number of iterations for data transfer (optional)")
parser.add_argument('--sleep', type=int, default=None, help="Sleep duration in seconds between iterations (optional)")
parser.add_argument('--bytes', type=int, default=None, help="Transfer a specific amount of data in bytes (optional)")
parser.add_argument('--constant_rate', action='store_true', help="Enable constant rate mode after normal transfer (optional)")
parser.add_argument('--normal_duration', type=int, default=5, help="Duration of normal data transfer before and after switching to constant rate (seconds)")

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
        max_throughput_mbps = 0  # To store the last increasing throughput for constant rate

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
                increasing_phase_end = start_time + args.normal_duration
                while time.time() < increasing_phase_end:
                    client_socket.sendall(DATA)
                    total_data_sent += len(DATA)
                    elapsed_time = time.time() - start_time
                    throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
                    max_throughput_mbps = max(max_throughput_mbps, throughput_mbps)

                # Log increasing phase progress
                print(f"[Client] Iteration {i+1}, Increasing Phase: Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Max Throughput: {max_throughput_mbps:.2f} Mbps")
                
                # Constant rate phase
                if args.constant_rate:
                    print(f"[Client] Iteration {i+1}, Constant Rate Phase: Maintaining {max_throughput_mbps:.2f} Mbps for {args.normal_duration} seconds.")
                    constant_phase_end = time.time() + args.normal_duration
                    bytes_per_second = max_throughput_mbps * 1024 * 1024 / 8

                    while time.time() < constant_phase_end:
                        client_socket.sendall(DATA[:min(BUFFER_SIZE, int(bytes_per_second))])
                        total_data_sent += min(BUFFER_SIZE, int(bytes_per_second))
                        time.sleep(1)

            # Log transfer progress
            elapsed_time = time.time() - start_time
            throughput_mbps = (total_data_sent * 8 / (1024 * 1024)) / elapsed_time
            print(f"[Client] Iteration {i+1}, Total Data sent: {total_data_sent / (1024 * 1024):.2f} MB, Throughput: {throughput_mbps:.2f} Mbps")

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

#python3 your_script_name.py -s 192.168.1.100 -p 5201 -t 10 --iterations 2 --normal_duration 10 --constant_rate
#Explanation of Command:
#-s 192.168.1.100: Specifies the server IP address (replace with your actual server IP).
#-p 5201: Sets the server port to 5201 (default value).
#-t 10: Sets the total duration of the increasing transfer phase to 10 seconds.
#--iterations 2: Runs the entire process for 2 iterations (increasing phase followed by constant rate phase, twice).
#--normal_duration 10: Sets both the increasing and constant phases to 10 seconds each.
#--constant_rate: Enables the constant rate phase after the increasing phase.
#Behavior:
#The client will first send data at an increasing rate for 10 seconds.
#It will then maintain the highest achieved rate for an additional 10 seconds.
#The process will repeat once more for 2 total iterations.

#python3 your_script_name.py -s 192.168.1.100 -p 5201 -t 10 --iterations 2 --normal_duration 10 --constant_rate --sleep 5
#Explanation of Command:
#--sleep 5: Adds a 5-second sleep interval between iterations.
#Behavior:
#The client will run an increasing rate phase for 10 seconds, followed by a constant rate phase for 10 seconds.
#After completing the first iteration, it will sleep for 5 seconds before starting the next iteration.
#This process will repeat for a total of 2 iterations.

#python3 your_script_name.py -s 192.168.1.100 -p 5201 -t 10 --iterations 2 --normal_duration 10 --sleep 5
#Explanation:
#--sleep 5: Adds a 5-second sleep interval between iterations.
#No --constant_rate: The script will sleep instead of maintaining a constant rate.
#The client will:
#Send data at an increasing rate for 10 seconds.
#Sleep for 5 seconds.
#Repeat this process for 2 total iterations.
