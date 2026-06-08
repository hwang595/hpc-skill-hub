#define _GNU_SOURCE

#include <mpi.h>
#include <omp.h>
#include <sched.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static void affinity_list(char *buffer, size_t length) {
  cpu_set_t set;
  int first = 1;
  size_t used = 0;

  if (length == 0) {
    return;
  }
  if (sched_getaffinity(0, sizeof(set), &set) != 0) {
    snprintf(buffer, length, "unavailable");
    return;
  }

  buffer[0] = '\0';
  for (int cpu = 0; cpu < CPU_SETSIZE; cpu++) {
    if (!CPU_ISSET(cpu, &set)) {
      continue;
    }
    int written = snprintf(
        buffer + used,
        length > used ? length - used : 0,
        "%s%d",
        first ? "" : ",",
        cpu);
    if (written < 0 || used >= length || (size_t)written >= length - used) {
      if (length > 4) {
        snprintf(buffer + length - 4, 4, "...");
      }
      return;
    }
    used += (size_t)written;
    first = 0;
  }

  if (first) {
    snprintf(buffer, length, "empty");
  }
}

int main(int argc, char **argv) {
  int rank = 0;
  int size = 0;
  char hostname[256] = "unknown";
  char processor[MPI_MAX_PROCESSOR_NAME] = "unknown";
  int processor_len = 0;
  int provided = 0;

  MPI_Init_thread(&argc, &argv, MPI_THREAD_FUNNELED, &provided);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);
  gethostname(hostname, sizeof(hostname));
  MPI_Get_processor_name(processor, &processor_len);
  processor[processor_len] = '\0';

  if (rank == 0) {
    printf("rank\tsize\thost\tprocessor\tthread\tthreads\tcpu\tomp_max_threads\tomp_num_procs\tmpi_thread_level\taffinity\n");
    fflush(stdout);
  }
  MPI_Barrier(MPI_COMM_WORLD);

  for (int current = 0; current < size; current++) {
    if (rank == current) {
#pragma omp parallel
      {
        char affinity[4096];
        affinity_list(affinity, sizeof(affinity));
#pragma omp critical
        {
          printf(
              "%d\t%d\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\n",
              rank,
              size,
              hostname,
              processor,
              omp_get_thread_num(),
              omp_get_num_threads(),
              sched_getcpu(),
              omp_get_max_threads(),
              omp_get_num_procs(),
              provided,
              affinity);
          fflush(stdout);
        }
      }
    }
    MPI_Barrier(MPI_COMM_WORLD);
  }

  MPI_Finalize();
  return 0;
}
