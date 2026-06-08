#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int env_int(const char *name, int fallback) {
  const char *value = getenv(name);
  if (value == NULL || value[0] == '\0') {
    return fallback;
  }
  int parsed = atoi(value);
  return parsed > 0 ? parsed : fallback;
}

static double pingpong_time(int rank, int peer, int tag, int bytes, int iterations) {
  char *buffer = (char *)malloc((size_t)bytes);
  if (buffer == NULL) {
    return -1.0;
  }
  memset(buffer, rank, (size_t)bytes);
  MPI_Barrier(MPI_COMM_WORLD);
  double start = MPI_Wtime();
  for (int i = 0; i < iterations; i++) {
    if (rank < peer) {
      MPI_Send(buffer, bytes, MPI_BYTE, peer, tag, MPI_COMM_WORLD);
      MPI_Recv(buffer, bytes, MPI_BYTE, peer, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    } else {
      MPI_Recv(buffer, bytes, MPI_BYTE, peer, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      MPI_Send(buffer, bytes, MPI_BYTE, peer, tag, MPI_COMM_WORLD);
    }
  }
  double elapsed = MPI_Wtime() - start;
  free(buffer);
  return elapsed / (double)(iterations * 2);
}

int main(int argc, char **argv) {
  int rank = 0;
  int size = 0;
  int name_len = 0;
  char host[256] = "unknown";
  char processor[MPI_MAX_PROCESSOR_NAME] = "unknown";
  int iterations = env_int("PROBE_ITERATIONS", 100);

  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);
  gethostname(host, sizeof(host));
  MPI_Get_processor_name(processor, &name_len);
  processor[name_len] = '\0';

  if (rank == 0) {
    printf("section\trank\tpeer\tsize\thost\tprocessor\tbytes\titerations\tseconds\tmetric\n");
    fflush(stdout);
  }
  MPI_Barrier(MPI_COMM_WORLD);

  for (int current = 0; current < size; current++) {
    if (rank == current) {
      printf("placement\t%d\t-1\t%d\t%s\t%s\t0\t%d\t0\tok\n", rank, size, host, processor, iterations);
      fflush(stdout);
    }
    MPI_Barrier(MPI_COMM_WORLD);
  }

  if (size >= 2) {
    if (rank == 0 || rank == 1) {
      double small = pingpong_time(rank, rank == 0 ? 1 : 0, 1001, 8, iterations);
      double large = pingpong_time(rank, rank == 0 ? 1 : 0, 1002, 1048576, iterations);
      if (rank == 0) {
        double bandwidth = large > 0.0 ? (1048576.0 / large) / (1024.0 * 1024.0) : 0.0;
        printf("pingpong\t0\t1\t%d\t%s\t%s\t8\t%d\t%.9f\tseconds_per_half_roundtrip\n", size, host, processor, iterations, small);
        printf("bandwidth\t0\t1\t%d\t%s\t%s\t1048576\t%d\t%.9f\tMiB_per_second\n", size, host, processor, iterations, bandwidth);
        fflush(stdout);
      }
    }
  }

  MPI_Finalize();
  return 0;
}
