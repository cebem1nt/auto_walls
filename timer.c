#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> // For sleep(), fork(), access(), readlink()
#include <sys/wait.h> // For waitpid()
#include <string.h>
#include <libgen.h> // For dirname()

#define MAX_PATH_LENGTH 4096
#define ERROR_EXIT(msg) { perror(msg); exit(EXIT_FAILURE); }

void execute_command(const char *command) {
    pid_t pid = fork();

    if (pid < 0) {
        ERROR_EXIT("fork() error");
    }

    if (pid == 0) {
        // Child process
        execlp("python3", "python3", command, (char *)NULL);
        // If execlp returns, an error occurred
        ERROR_EXIT("execlp() error");
    } else {
        // Parent process
        int status;
        if (waitpid(pid, &status, 0) == -1) {
            ERROR_EXIT("waitpid() error");
        }
        if (WIFEXITED(status)) {
            printf("Child process exited with status %d\n", WEXITSTATUS(status));
        } else {
            printf("Child process terminated abnormally\n");
        }
    }
}

void timer(int secs, const char *script_dir) {
    while (1) {
        sleep(secs * 60);

        // Build the command string
        char command[MAX_PATH_LENGTH];
        snprintf(command, sizeof(command), "%s/set_next.py", script_dir);

        // Check if the file exists
        if (access(command, F_OK) != 0) {
            fprintf(stderr, "File %s does not exist.\n", command);
            continue;
        }

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

    // Get the directory of the currently running executable
    char exe_path[MAX_PATH_LENGTH];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len == -1) {
        ERROR_EXIT("readlink() error");
    }
    exe_path[len] = '\0'; // Null-terminate the path

    // Extract the directory from the executable path
    char *dir = dirname(exe_path);

    // Start the timer with the directory containing set_next.py
    timer(time, dir);

    return EXIT_SUCCESS;
}
