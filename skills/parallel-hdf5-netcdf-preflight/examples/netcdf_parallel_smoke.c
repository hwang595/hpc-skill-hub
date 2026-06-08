#include <mpi.h>
#include <netcdf.h>

#include <stdio.h>
#include <stdlib.h>

static void check(int status, const char *step) {
    if (status != NC_NOERR) {
        fprintf(stderr, "%s: %s\n", step, nc_strerror(status));
        MPI_Abort(MPI_COMM_WORLD, status);
    }
}

int main(int argc, char **argv) {
    int rank = 0;
    int size = 1;
    const char *path = "netcdf-parallel-smoke.nc";
    int ncid = -1;
    int dimid = -1;
    int varid = -1;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc > 1) {
        path = argv[1];
    }

    check(nc_create_par(path, NC_CLOBBER | NC_NETCDF4 | NC_MPIIO,
                        MPI_COMM_WORLD, MPI_INFO_NULL, &ncid),
          "nc_create_par");
    check(nc_def_dim(ncid, "rank", (size_t)size, &dimid), "nc_def_dim");
    check(nc_def_var(ncid, "rank", NC_INT, 1, &dimid, &varid), "nc_def_var");
    check(nc_enddef(ncid), "nc_enddef");
    check(nc_var_par_access(ncid, varid, NC_COLLECTIVE), "nc_var_par_access");

    size_t start[1] = {(size_t)rank};
    size_t count[1] = {1};
    int value = rank;
    check(nc_put_vara_int(ncid, varid, start, count, &value), "nc_put_vara_int");
    check(nc_close(ncid), "nc_close");

    if (rank == 0) {
        printf("wrote %s with %d ranks\n", path, size);
    }

    MPI_Finalize();
    return EXIT_SUCCESS;
}
