#!/usr/bin/env bash
set -euo pipefail

app_dir="${1:-examples/batch-connect-app}"

echo "app_dir=${app_dir}"

required_files=(
  "manifest.yml"
  "form.yml.erb"
  "submit.yml.erb"
  "template/script.sh"
)

for file in "${required_files[@]}"; do
  if [ ! -f "${app_dir}/${file}" ]; then
    echo "ERROR: missing ${file}" >&2
    exit 1
  fi
done

echo "== files =="
find "${app_dir}" -maxdepth 3 -type f | sort

echo "== placeholder review =="
grep -RIn "<cluster-id>\\|<account>\\|<debug-partition>\\|<module>" "${app_dir}" || true

echo "== native scheduler arguments =="
if grep -RIn "native:" "${app_dir}"; then
  echo "Review native arguments carefully; prefer portable script fields where possible."
else
  echo "No native scheduler arguments found."
fi

echo "== shell syntax =="
if [ -f "${app_dir}/template/script.sh" ]; then
  bash -n "${app_dir}/template/script.sh"
fi
if [ -f "${app_dir}/template/before.sh.erb" ]; then
  bash -n "${app_dir}/template/before.sh.erb"
fi

echo "Batch Connect skeleton review checks completed."
