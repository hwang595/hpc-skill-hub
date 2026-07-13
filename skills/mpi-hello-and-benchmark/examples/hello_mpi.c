#include <mpi.h>
#include <stdio.h>
#include <unistd.h>

int main(int argc, char **argv) {
    int rank = 0;
    int size = 0;
    char host[256];

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    if (gethostname(host, sizeof(host)) != 0) {
        snprintf(host, sizeof(host), "unknown");
    }
    host[sizeof(host) - 1] = '\0';

    printf("rank %d of %d on %s\n", rank, size, host);

    MPI_Finalize();
    return 0;
}
