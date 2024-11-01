#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>

#define SERVER_PORT 5201
#define BUFFER_SIZE 128 * 1024  // 128 KB buffer size
#define INTERVAL 0.01           // 10 ms interval for pacing

void handle_error(const char *msg) {
    perror(msg);
    exit(EXIT_FAILURE);
}

void normal_mode(int client_socket) {
    char buffer[BUFFER_SIZE];
    ssize_t bytes_received;
    size_t total_data_received = 0;

    printf("Normal mode: client is sending data to server.\n");

    while ((bytes_received = recv(client_socket, buffer, BUFFER_SIZE, 0)) > 0) {
        total_data_received += bytes_received;
    }

    printf("Total data received: %.2f MB\n", total_data_received / (1024.0 * 1024.0));

    if (bytes_received < 0) {
        handle_error("recv failed");
    }
}

void reverse_mode(int client_socket, int iterations, int sleep_duration, int consphase_time, 
                  int target_rate, int rate_based_phase, int time_based_phase, int bytes, int time_sec) {
    char data[BUFFER_SIZE];
    memset(data, 'X', BUFFER_SIZE);
    size_t total_data_sent = 0;
    float current_byte_send = 0;
    struct timespec req, rem;
    req.tv_sec = 0;
    req.tv_nsec = INTERVAL * 1e9;

    for (int i = 0; i < iterations; i++) {
        total_data_sent = 0;
        printf("[Server] Iteration %d started.\n", i + 1);

        // Phase 1: Increasing Phase
        if (rate_based_phase && target_rate) {
            printf("[Server] Increasing phase based on target rate.\n");
            if (i == 0) {
                current_byte_send = target_rate * (1024 * 1024) / 8;
            } else {
                current_byte_send = target_rate * (1 + 0.2 * i) * (1024 * 1024) / 8;
            }

            size_t bytes_to_send = current_byte_send;

            while (total_data_sent < bytes_to_send) {
                size_t chunk_size = (bytes_to_send - total_data_sent) > BUFFER_SIZE ? BUFFER_SIZE : (bytes_to_send - total_data_sent);
                if (send(client_socket, data, chunk_size, 0) < 0) {
                    handle_error("send failed");
                }
                total_data_sent += chunk_size;
            }

            printf("[Server] Increasing phase ended, total_data_sent = %.2f MB\n", total_data_sent / (1024.0 * 1024.0));
        }

        // Phase 2: Constant Rate Phase
        printf("[Server] Constant rate phase started.\n");
        size_t bytes_per_second = current_byte_send / consphase_time;
        size_t bytes_per_interval = bytes_per_second * INTERVAL;
        size_t constant_phase_data_sent = 0;

        clock_t start_time = clock();
        clock_t constant_phase_end = start_time + consphase_time * CLOCKS_PER_SEC;

        while (clock() < constant_phase_end) {
            size_t remaining_bytes = current_byte_send - constant_phase_data_sent;
            if (remaining_bytes <= 0) {
                break;
            }

            size_t chunk_size = remaining_bytes > bytes_per_interval ? bytes_per_interval : remaining_bytes;
            if (send(client_socket, data, chunk_size, 0) < 0) {
                handle_error("send failed");
            }
            constant_phase_data_sent += chunk_size;

            nanosleep(&req, &rem);  // Pacing
        }

        total_data_sent += constant_phase_data_sent;
        printf("[Server] Constant rate ended: total_data_sent = %.2f MB\n", total_data_sent / (1024.0 * 1024.0));

        // Sleep between iterations
        if (sleep_duration > 0) {
            printf("[Server] Sleeping for %d seconds.\n", sleep_duration);
            sleep(sleep_duration);
        }
    }
}

int main(int argc, char *argv[]) {
    int server_socket, client_socket;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_len = sizeof(client_addr);
    char mode;

    // Server socket setup
    if ((server_socket = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        handle_error("socket creation failed");
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(SERVER_PORT);

    if (bind(server_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        handle_error("bind failed");
    }

    if (listen(server_socket, 1) < 0) {
        handle_error("listen failed");
    }

    printf("Server is listening on port %d\n", SERVER_PORT);

    // Accept client connection
    if ((client_socket = accept(server_socket, (struct sockaddr *)&client_addr, &client_addr_len)) < 0) {
        handle_error("accept failed");
    }

    printf("Client connected.\n");

    // Receive mode instruction from client
    if (recv(client_socket, &mode, 1, 0) <= 0) {
        handle_error("recv failed");
    }

    if (mode == 'N') {
        normal_mode(client_socket);
    } else if (mode == 'R') {
        // Example parameters for reverse mode
        reverse_mode(client_socket, 1, 0, 5, 100, 1, 0, 0, 0);
    } else {
        printf("Invalid mode received.\n");
        close(client_socket);
        close(server_socket);
        exit(EXIT_FAILURE);
    }

    // Close sockets
    close(client_socket);
    close(server_socket);

    return 0;
}
