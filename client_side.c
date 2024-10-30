#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <getopt.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <time.h>

#define BUFFER_SIZE 131072  // 128 KB

void handle_server(int client_socket, int iterations, int sleep_duration, int constant_rate,
                   int phase_time, int target_rate, int rate_based_phase, int time_based_phase,
                   int bytes, int duration, int reverse_mode);

int main(int argc, char *argv[]) {
    int client_socket, port = 5201;
    struct sockaddr_in server_addr;
    char *server_ip = NULL;

    // Variables for options
    int iterations = 1, sleep_duration = 0, constant_rate = 0;
    int phase_time = 5, target_rate = 0, rate_based_phase = 0;
    int time_based_phase = 0, bytes = 0, duration = 0, reverse_mode = 0;

    // Command-line options
    static struct option long_options[] = {
        {"server", required_argument, 0, 's'},
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
    while ((opt = getopt_long(argc, argv, "s:p:i:S:c:t:T:b:d:rC", long_options, &option_index)) != -1) {
        switch (opt) {
            case 's':
                server_ip = optarg;
                break;
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

    if (server_ip == NULL) {
        fprintf(stderr, "Server IP is required\n");
        exit(EXIT_FAILURE);
    }

    // Create a TCP socket
    client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    // Set up the server address structure
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    if (inet_pton(AF_INET, server_ip, &server_addr.sin_addr) <= 0) {
        perror("Invalid server IP address");
        close(client_socket);
        exit(EXIT_FAILURE);
    }

    // Connect to the server
    if (connect(client_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Connection to server failed");
        close(client_socket);
        exit(EXIT_FAILURE);
    }

    printf("Connected to server at %s:%d\n", server_ip, port);

    // Send mode to the server ('N' for Normal, 'R' for Reverse)
    char mode = reverse_mode ? 'R' : 'N';
    send(client_socket, &mode, sizeof(mode), 0);

    // Handle server communication based on options
    handle_server(client_socket, iterations, sleep_duration, constant_rate,
                  phase_time, target_rate, rate_based_phase, time_based_phase,
                  bytes, duration, reverse_mode);

    // Close the socket
    close(client_socket);
    printf("Connection closed.\n");
    return 0;
}

void handle_server(int client_socket, int iterations, int sleep_duration, int constant_rate,
                   int phase_time, int target_rate, int rate_based_phase, int time_based_phase,
                   int bytes, int duration, int reverse_mode) {
    char buffer[BUFFER_SIZE];
    memset(buffer, 'X', BUFFER_SIZE);

    if (reverse_mode) {
        printf("Reverse Mode: Receiving data from the server.\n");

        int total_data_received = 0;
        time_t start_time = time(NULL);

        while (1) {
            int bytes_received = recv(client_socket, buffer, BUFFER_SIZE, 0);
            if (bytes_received <= 0) {
                break;  // Server closed connection or error occurred
            }
            total_data_received += bytes_received;
        }

        double elapsed_time = difftime(time(NULL), start_time);
        double throughput_mbps = (total_data_received * 8.0) / (elapsed_time * 1024 * 1024);
        printf("Total data received: %.2f MB, Throughput: %.2f Mbps\n",
               total_data_received / (1024.0 * 1024), throughput_mbps);

    } else {
        printf("Normal Mode: Sending data to the server.\n");

        int total_data_sent = 0;
        double max_throughput_mbps = 0.0;

        for (int i = 0; i < iterations; i++) {
            printf("[Client] Iteration %d started\n", i + 1);
            time_t start_time = time(NULL);
            int bytes_sent = 0;

            // Phase 1: Increasing Phase
            if (constant_rate) {
                int target_bytes = (target_rate * 1024 * 1024) / 8;

                if (rate_based_phase) {
                    while (bytes_sent < target_bytes) {
                        send(client_socket, buffer, BUFFER_SIZE, 0);
                        bytes_sent += BUFFER_SIZE;
                    }
                } else if (time_based_phase > 0) {
                    time_t phase_end_time = start_time + time_based_phase;
                    while (time(NULL) < phase_end_time) {
                        send(client_socket, buffer, BUFFER_SIZE, 0);
                        bytes_sent += BUFFER_SIZE;
                    }
                }

                double elapsed_time = difftime(time(NULL), start_time);
                max_throughput_mbps = (bytes_sent * 8.0) / (elapsed_time * 1024 * 1024);
                printf("[Client] Increasing phase ended: max_throughput = %.2f Mbps\n", max_throughput_mbps);

                // Phase 2: Constant Rate Phase
                time_t constant_start_time = time(NULL);
                while (difftime(time(NULL), constant_start_time) < phase_time) {
                    send(client_socket, buffer, BUFFER_SIZE, 0);
                }
                printf("[Client] Constant rate phase ended.\n");
            }

            // Sleep between iterations
            if (sleep_duration > 0) {
                printf("[Client] Iteration %d: Sleeping for %d seconds\n", i + 1, sleep_duration);
                sleep(sleep_duration);
            }
        }
    }
}
