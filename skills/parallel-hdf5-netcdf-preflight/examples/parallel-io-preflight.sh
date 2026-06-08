#!/usr/bin/env bash
set -euo pipefail

output_dir="${OUTPUT_DIR:-parallel-io-preflight-report}"
scratch_dir="${SCRATCH_DIR:-<approved-scratch-or-project-path>}"
mpi_tasks="${MPI_TASKS:-2}"
script_dir="${BASH_SOURCE[0]%/*}"
if [ "${script_dir}" = "${BASH_SOURCE[0]}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"
hdf5_source="${script_dir}/hdf5_mpi_smoke.c"
netcdf_source="${script_dir}/netcdf_parallel_smoke.c"

mkdir -p "${output_dir}"

capture() {
  output_file="$1"
  shift
  {
    printf '# command\n'
    printf '%q ' "$@"
    printf '\n\n'
    "$@"
  } > "${output_file}" 2>&1 || {
    status="$?"
    {
      printf '\nWARN: command exited with status %s\n' "${status}"
      printf 'Review local module and wrapper availability before scaling.\n'
    } >> "${output_file}"
  }
}

record_tool() {
  tool_name="$1"
  output_file="$2"
  if command -v "${tool_name}" >/dev/null 2>&1; then
    {
      printf '%s=%s\n' "${tool_name}" "$(command -v "${tool_name}")"
      "${tool_name}" --version 2>/dev/null || true
    } > "${output_file}"
  else
    printf '%s=not-found\n' "${tool_name}" > "${output_file}"
  fi
}

for tool in mpicc h5pcc h5cc h5dump nc-config ncdump srun; do
  record_tool "${tool}" "${output_dir}/${tool}.txt"
done

if command -v mpicc >/dev/null 2>&1; then
  capture "${output_dir}/mpicc-show.txt" mpicc -show
fi

if command -v h5pcc >/dev/null 2>&1; then
  capture "${output_dir}/h5pcc-showconfig.txt" h5pcc -showconfig
  capture "${output_dir}/h5pcc-show.txt" h5pcc -show
elif command -v h5cc >/dev/null 2>&1; then
  capture "${output_dir}/h5cc-showconfig.txt" h5cc -showconfig
  capture "${output_dir}/h5cc-show.txt" h5cc -show
fi

if command -v nc-config >/dev/null 2>&1; then
  capture "${output_dir}/nc-config-all.txt" nc-config --all
  capture "${output_dir}/nc-config-parallel4.txt" nc-config --has-parallel4
  capture "${output_dir}/nc-config-parallel.txt" nc-config --has-parallel
fi

cat > "${output_dir}/build-and-run-plan.sh" <<PLAN
#!/usr/bin/env bash
set -euo pipefail

# Review modules, account, partition, and scratch path before running.
scratch_dir="${scratch_dir}"
mpi_tasks="${mpi_tasks}"
mkdir -p "\${scratch_dir}"

# Parallel HDF5 smoke test. Prefer h5pcc because it should carry HDF5 include,
# library, and MPI wrapper settings from the active module environment.
hdf5_source="${hdf5_source}"
h5pcc "\${hdf5_source}" -o "\${scratch_dir}/hdf5_mpi_smoke"
srun -n "\${mpi_tasks}" "\${scratch_dir}/hdf5_mpi_smoke" "\${scratch_dir}/hdf5-mpi-smoke.h5"
h5dump -H "\${scratch_dir}/hdf5-mpi-smoke.h5"

# NetCDF parallel smoke test. nc-config supplies netCDF include and library
# flags; mpicc supplies the MPI compiler wrapper.
netcdf_source="${netcdf_source}"
mpicc "\${netcdf_source}" \$(nc-config --cflags --libs) -o "\${scratch_dir}/netcdf_parallel_smoke"
srun -n "\${mpi_tasks}" "\${scratch_dir}/netcdf_parallel_smoke" "\${scratch_dir}/netcdf-parallel-smoke.nc"
ncdump -h "\${scratch_dir}/netcdf-parallel-smoke.nc"
PLAN
chmod +x "${output_dir}/build-and-run-plan.sh"

cat > "${output_dir}/summary.md" <<SUMMARY
# Parallel HDF5 NetCDF Preflight

- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Output directory: ${output_dir}
- Scratch directory placeholder: ${scratch_dir}
- Planned MPI tasks: ${mpi_tasks}

## Review

- Check whether \`h5pcc -showconfig\` reports parallel HDF5 support.
- Check whether \`nc-config --all\` and parallel capability flags match the
  module you intended to load.
- Confirm \`mpicc\`, HDF5, and NetCDF wrappers come from compatible compiler
  and MPI families.
- Run the generated build plan only in a short test allocation and on an
  approved scratch or project filesystem.
SUMMARY

echo "wrote report_dir=${output_dir}"
echo "review ${output_dir}/build-and-run-plan.sh before running smoke tests"
