#include <mpi.h>
#include "hdf5.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    int rank = 0;
    int size = 1;
    const char *path = "hdf5-mpi-smoke.h5";

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc > 1) {
        path = argv[1];
    }

    hid_t access_plist = H5Pcreate(H5P_FILE_ACCESS);
    H5Pset_fapl_mpio(access_plist, MPI_COMM_WORLD, MPI_INFO_NULL);

    hid_t file = H5Fcreate(path, H5F_ACC_TRUNC, H5P_DEFAULT, access_plist);
    H5Pclose(access_plist);

    hsize_t dims[1] = {(hsize_t)size};
    hid_t filespace = H5Screate_simple(1, dims, NULL);
    hid_t dataset = H5Dcreate2(file, "rank", H5T_NATIVE_INT, filespace,
                               H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);

    hsize_t offset[1] = {(hsize_t)rank};
    hsize_t count[1] = {1};
    H5Sselect_hyperslab(filespace, H5S_SELECT_SET, offset, NULL, count, NULL);

    hid_t memspace = H5Screate_simple(1, count, NULL);
    hid_t transfer_plist = H5Pcreate(H5P_DATASET_XFER);
    H5Pset_dxpl_mpio(transfer_plist, H5FD_MPIO_COLLECTIVE);

    int value = rank;
    herr_t status = H5Dwrite(dataset, H5T_NATIVE_INT, memspace, filespace,
                             transfer_plist, &value);

    H5Pclose(transfer_plist);
    H5Sclose(memspace);
    H5Dclose(dataset);
    H5Sclose(filespace);
    H5Fclose(file);

    if (rank == 0) {
        printf("wrote %s with %d ranks\n", path, size);
    }

    MPI_Finalize();
    return status < 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}
