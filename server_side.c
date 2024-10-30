#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <getopt.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/time.h>
#include <time.h>

#define BUFFER_SIZE 131072  // 128 KB

// Function to handle the client connection
void handle_client(int client_socket, int iterations, int sleep_duration, int constant_rate,
                   int phase_time, int target_rate, int rate_based_phase, int time_based_phase,
                   int bytes, int duration, int reverse_mode);

// Main function
int main(int argc, char *argv[]) {
    int server_socket, client_socket, port = 5201;
    struct sockaddr_in server_addr, client_addr;
    socklen_t addr_len = sizeof(client_addr);

    // Variables for options
    int iterations = 1, sleep_duration = 0, constant_rate = 0;
    int phase_time = 5, target_rate = 0, rate_based_phase = 0;
    int time_based_phase = 0, bytes = 0, duration = 0, reverse_mode = 0;

    // Command-line options
    static struct option long_options[] = {
        {"port", required_argument, 0, 'p'},
        {"iterations", required_argument, 0, 'i'},
        {"sleep", required_argument, 0, 'S'},
        {"constant_rate", no_argument, 0, 'C'},
        {"phase_time", required_argument, 0, 'c'},
        {"target_rate", required_argument, 0, 't'},
        {"rate_based_phase", no_argument, 0, 'R'},
        {"time_based_phase", required_argument, 0, 'T'},
        {"bytes", required_argument, 0, 'b'},
        {"time", required_argument, 0, 'd'},
        {"reverse", no_argument, 0, 'r'},
        {0, 0, 0, 0}
    };

    int option_index = 0, opt;
    while ((opt = getopt_long(argc, argv, "p:i:S:c:t:T:b:d:rC", long_options, &option_index)) != -1) {
        switch (opt) {
            case 'p':
                port = atoi(optarg);
                break;
            case 'i':
                iterations = atoi(optarg);
                break;
            case 'S':
                sleep_duration = atoi(optarg);
                break;
            case 'c':
                phase_time = atoi(optarg);
                break;
            case 't':
                target_rate = atoi(optarg);
                break;
            case 'T':
                time_based_phase = atoi(optarg);
                break;
            case 'b':
                bytes = atoi(optarg);
                break;
            case 'd':
                duration = atoi(optarg);
                break;
            case 'C':
                constant_rate = 1;
                break;
            case 'R':
                rate_based_phase = 1;
                break;
            case 'r':
                reverse_mode = 1;
                break;
            default:
                fprintf(stderr, "Invalid option\n");
                exit(EXIT_FAILURE);
        }
    }

    // Create a TCP socket
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    // Set up the server address structure
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    // Bind the socket to the specified port
    if (bind(server_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        close(server_socket);
        exit(EXIT_FAILURE);
    }

    // Listen for incoming connections
    if (listen(server_socket, 5) < 0) {
        perror("Listen failed");
        close(server_socket);
        exit(EXIT_FAILURE);
    }

    printf("Server is listening on 0.0.0.0:%d\n", port);

    // Accept a client connection
    client_socket = accept(server_socket, (struct sockaddr *)&client_addr, &addr_len);
    if (client_socket < 0) {
        perror("Client accept failed");
        close(server_socket);
        exit(EXIT_FAILURE);
    }

    printf("Client connected.\n");

    // Handle the client connection
    handle_client(client_socket, iterations, sleep_duration, constant_rate,
                  phase_time, target_rate, rate_based_phase, time_based_phase,
                  bytes, duration, reverse_mode);

    // Close the sockets
    close(client_socket);
    close(server_socket);
    return 0;
}

// Function to handle client connection and data transfer
void handle_client(int client_socket, int iterations, int sleep_duration, int constant_rate,
                   int phase_time, int target_rate, int rate_based_phase, int time_based_phase,
                   int bytes, int duration, int reverse_mode) {
    char buffer[BUFFER_SIZE];
    memset(buffer, 'X', BUFFER_SIZE);

    if (reverse_mode) {
        printf("Reverse Mode: Sending data to the client.\n");

        for (int iter = 0; iter < iterations; iter++) {
            printf("[Server] Iteration %d started\n", iter + 1);

            // Increasing Phase
            double total_data_sent = 0;
            double target_bytes = (target_rate * 1024 * 1024) / 8;  // Convert target rate from Mbps to bytes/sec
            struct timeval start_time, current_time;
            gettimeofday(&start_time, NULL);

            while (total_data_sent < target_bytes) {
                // Calculate remaining bytes to send
                ssize_t remaining_bytes = target_bytes - total_data_sent;
                ssize_t chunk_size = remaining_bytes < BUFFER_SIZE ? remaining_bytes : BUFFER_SIZE;

                // Send data in chunks, capping at target_bytes
                ssize_t sent_bytes = send(client_socket, buffer, chunk_size, 0);
                if (sent_bytes <= 0) {
                    perror("Error sending data");
                    break;
                }
                total_data_sent += sent_bytes;

                // Break the loop if we've reached the target bytes
                if (total_data_sent >= target_bytes) {
                    break;
                }

                // Calculate elapsed time for progress reporting
                gettimeofday(&current_time, NULL);
                double elapsed_time = (current_time.tv_sec - start_time.tv_sec) +
                                      (current_time.tv_usec - start_time.tv_usec) / 1000000.0;

                // Print real-time progress
                if (elapsed_time > 0) {
                    double throughput_mbps = (total_data_sent * 8) / (1024 * 1024 * elapsed_time);
                    printf("\r[Server] Current throughput: %.2f Mbps, Total sent: %.2f MB", 
                           throughput_mbps, total_data_sent / (1024.0 * 1024.0));
                    fflush(stdout);
                }
            }

            // Print the final result after increasing phase
            printf("\n[Server] Increasing phase ended, total_data_sent = %.2f MB\n", total_data_sent / (1024.0 * 1024.0));


            // Constant Rate Phase
            double bytes_per_second = (target_rate * 1024 * 1024) / 8;
            gettimeofday(&start_time, NULL);

            while (1) {
                gettimeofday(&current_time, NULL);
                double elapsed_time = (current_time.tv_sec - start_time.tv_sec) +
                                      (current_time.tv_usec - start_time.tv_usec) / 1000000.0;

                if (elapsed_time >= phase_time) break;

                ssize_t sent_bytes = send(client_socket, buffer, (size_t)bytes_per_second, 0);
                if (sent_bytes <= 0) {
                    perror("Error sending data");
                    break;
                }
            }

            printf("[Server] Constant rate phase ended.\n");

            // Update the target rate for the next iteration (increase by 20%)
            target_rate = target_rate + (target_rate * 0.2);

            // Sleep between iterations if specified
            if (sleep_duration > 0) {
                printf("[Server] Iteration %d: Sleeping for %d seconds\n", iter + 1, sleep_duration);
                sleep(sleep_duration);
            }
        }
    } else {
        printf("Normal Mode: Receiving data from the client.\n");

        int total_data_received = 0;
        while (1) {
            int bytes_received = recv(client_socket, buffer, BUFFER_SIZE, 0);
            if (bytes_received <= 0) {
                break;  // Client closed connection or error occurred
            }
            total_data_received += bytes_received;
        }

        double throughput_mbps = (total_data_received * 8.0) / (1024 * 1024);
        printf("Total data received: %.2f MB, Throughput: %.2f Mbps\n",
               total_data_received / (1024.0 * 1024), throughput_mbps);
    }
}
