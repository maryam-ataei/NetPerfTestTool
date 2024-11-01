#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>

#define BUFFER_SIZE 128 * 1024  // Default buffer size (128 KB)
#define SERVER_PORT 5201

void handle_error(const char *msg) {
    perror(msg);
    exit(EXIT_FAILURE);
}

void reverse_mode(int client_socket, size_t buffer_size) {
    char buffer[buffer_size];
    ssize_t bytes_received;
    size_t total_data_received = 0;
    clock_t start_time = clock();

    printf("Reverse Mode: Receiving data from the server.\n");

    while ((bytes_received = recv(client_socket, buffer, buffer_size, 0)) > 0) {
        total_data_received += bytes_received;
    }

    if (bytes_received < 0) {
        handle_error("recv failed");
    }

    double elapsed_time = (double)(clock() - start_time) / CLOCKS_PER_SEC;
    double throughput_mbps = (total_data_received * 8) / (1024.0 * 1024.0 * elapsed_time);

    printf("Total data received: %.2f MB, Throughput: %.2f Mbps\n",
           total_data_received / (1024.0 * 1024.0), throughput_mbps);
}

void normal_mode(int client_socket, int iterations, int sleep_duration, int constant_rate, int phase_time,
                 int target_rate, int rate_based_phase, int time_based_phase, int bytes, int time_sec,
                 size_t buffer_size) {
    char data[buffer_size];
    memset(data, 'X', buffer_size);

    for (int i = 0; i < iterations; i++) {
        size_t total_data_sent = 0;
        clock_t start_time = clock();
        double max_throughput_mbps = 0;

        printf("[Client] Iteration %d started.\n", i + 1);

        // Phase 1: Increasing Phase
        if (constant_rate) {
            if (rate_based_phase && target_rate) {
                printf("[Client] Increasing phase based on target rate.\n");

                while (max_throughput_mbps < target_rate) {
                    if (send(client_socket, data, buffer_size, 0) < 0) {
                        handle_error("send failed");
                    }
                    total_data_sent += buffer_size;
                    double elapsed_time = (double)(clock() - start_time) / CLOCKS_PER_SEC;
                    max_throughput_mbps = (total_data_sent * 8) / (1024.0 * 1024.0 * elapsed_time);
                }
            } else if (time_based_phase) {
                printf("[Client] Increasing phase based on time.\n");

                clock_t phase_end_time = start_time + time_based_phase * CLOCKS_PER_SEC;
                while (clock() < phase_end_time) {
                    if (send(client_socket, data, buffer_size, 0) < 0) {
                        handle_error("send failed");
                    }
                    total_data_sent += buffer_size;
                }
            }

            // Phase 2: Constant Rate Phase
            clock_t constant_phase_end = clock() + phase_time * CLOCKS_PER_SEC;
            size_t bytes_per_second = max_throughput_mbps * 1024 * 1024 / 8;
            size_t bytes_per_interval = bytes_per_second * 0.01;

            printf("[Client] Constant rate phase started.\n");
            while (clock() < constant_phase_end) {
                size_t chunk_size = buffer_size < bytes_per_interval ? buffer_size : bytes_per_interval;
                if (send(client_socket, data, chunk_size, 0) < 0) {
                    handle_error("send failed");
                }
                total_data_sent += chunk_size;

                usleep(10000);  // Sleep for 10 ms
            }
        } else {
            // Non-constant rate, either bytes or time-based transfer
            if (bytes > 0) {
                printf("[Client] Sending %d bytes.\n", bytes);
                size_t bytes_to_send = bytes;
                while (bytes_to_send > 0) {
                    size_t chunk_size = buffer_size < bytes_to_send ? buffer_size : bytes_to_send;
                    if (send(client_socket, data, chunk_size, 0) < 0) {
                        handle_error("send failed");
                    }
                    total_data_sent += chunk_size;
                    bytes_to_send -= chunk_size;
                }
            } else if (time_sec > 0) {
                printf("[Client] Sending data for %d seconds.\n", time_sec);
                clock_t phase_end_time = clock() + time_sec * CLOCKS_PER_SEC;
                while (clock() < phase_end_time) {
                    if (send(client_socket, data, buffer_size, 0) < 0) {
                        handle_error("send failed");
                    }
                    total_data_sent += buffer_size;
                }
            }
        }

        // Log transfer progress
        double elapsed_time = (double)(clock() - start_time) / CLOCKS_PER_SEC;
        double throughput_mbps = (total_data_sent * 8) / (1024.0 * 1024.0 * elapsed_time);

        printf("[Client] Iteration %d completed, Data sent: %.2f MB, Throughput: %.2f Mbps\n",
               i + 1, total_data_sent / (1024.0 * 1024.0), throughput_mbps);

        // Sleep between iterations
        if (sleep_duration > 0) {
            printf("[Client] Sleeping for %d seconds.\n", sleep_duration);
            sleep(sleep_duration);
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s -s <server_ip> [options]\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    char *server_ip = NULL;
    int server_port = SERVER_PORT;
    int reverse = 0, iterations = 1, sleep_duration = 0, constant_rate = 0;
    int phase_time = 5, target_rate = 0, rate_based_phase = 0, time_based_phase = 0, bytes = 0, time_sec = 0;
    size_t buffer_size = BUFFER_SIZE;

    // Parse command-line arguments
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-s") == 0 && i + 1 < argc) {
            server_ip = argv[++i];
        } else if (strcmp(argv[i], "-p") == 0 && i + 1 < argc) {
            server_port = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-R") == 0) {
            reverse = 1;
        } else if (strcmp(argv[i], "--iterations") == 0 && i + 1 < argc) {
            iterations = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--sleep") == 0 && i + 1 < argc) {
            sleep_duration = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--constant_rate") == 0) {
            constant_rate = 1;
        } else if (strcmp(argv[i], "--phase_time") == 0 && i + 1 < argc) {
            phase_time = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--target_rate") == 0 && i + 1 < argc) {
            target_rate = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--rate_based_phase") == 0) {
            rate_based_phase = 1;
        } else if (strcmp(argv[i], "--time_based_phase") == 0 && i + 1 < argc) {
            time_based_phase = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--bytes") == 0 && i + 1 < argc) {
            bytes = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--time") == 0 && i + 1 < argc) {
            time_sec = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--buffer_size") == 0 && i + 1 < argc) {
            buffer_size = atoi(argv[++i]);
        }
    }

    if (!server_ip) {
        fprintf(stderr, "Server IP address is required.\n");
        exit(EXIT_FAILURE);
    }

    int client_socket;
    struct sockaddr_in server_addr;

    // Create a TCP socket
    if ((client_socket = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        handle_error("socket creation failed");
    }

    // Set server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(server_port);
    if (inet_pton(AF_INET, server_ip, &server_addr.sin_addr) <= 0) {
        handle_error("invalid address");
    }

    // Connect to the server
    if (connect(client_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        handle_error("connection failed");
    }

    printf("Connected to server at %s:%d\n", server_ip, server_port);

    // Send mode to the server ('N' for Normal, 'R' for Reverse)
    char mode = reverse ? 'R' : 'N';
    if (send(client_socket, &mode, 1, 0) < 0) {
        handle_error("send failed");
    }

    if (reverse) {
        reverse_mode(client_socket, buffer_size);
    } else {
        normal_mode(client_socket, iterations, sleep_duration, constant_rate, phase_time,
                    target_rate, rate_based_phase, time_based_phase, bytes, time_sec, buffer_size);
    }

    // Close the client socket
    close(client_socket);
    printf("Connection closed.\n");

    return 0;
}
