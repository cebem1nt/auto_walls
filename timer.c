#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> // For sleep() and fork()
#include <string.h>
#include <sys/wait.h> // For waitpid()

// Define a reasonable buffer size if PATH_MAX is not available
#define MAX_PATH_LENGTH 4096

void execute_command(const char *command) {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork() error");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) {
        // Child process
        execlp("python3", "python3", command, (char *)NULL);
        // If execlp returns, an error occurred
        perror("execlp() error");
        exit(EXIT_FAILURE);
    } else {
        // Parent process
        int status;
        waitpid(pid, &status, 0); // Wait for child process to complete
        if (WIFEXITED(status)) {
            printf("Child process exited with status %d\n", WEXITSTATUS(status));
        } else {
            printf("Child process terminated abnormally\n");
        }
    }
}

void timer(int secs) {
    char current_dir[MAX_PATH_LENGTH];
    if (getcwd(current_dir, sizeof(current_dir)) == NULL) {
        perror("getcwd() error");
        exit(EXIT_FAILURE);
    }
    
    while (1) {
        sleep(secs * 60);

        // Build the command string
        char command[MAX_PATH_LENGTH + 20];
        snprintf(command, sizeof(command), "%s/set_next.py", current_dir);

        // Execute the command
        execute_command(command);
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <time>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int time = atoi(argv[1]);
    if (time <= 0) {
        fprintf(stderr, "Invalid time argument. It must be a positive integer.\n");
        return EXIT_FAILURE;
    }

    timer(time);
    return EXIT_SUCCESS;
}
