#!/usr/bin/env bash
# Script to create input_data/[POD name] directories for testing
# Require bash due to lingering conda compatibility issues.
## @author wrongkindofdoctor
## Report problems using the MDTF-diagnostics Issue Board:
## https://github.com/NOAA-GFDL/MDTF-diagnostics/issues

# exit immediately if pipe fails and trap errors
set -Eeo pipefail

# define array of POD directory names
declare -a pod_names=(
                     "example"
                     "Wheeler_Kiladis"
                     "EOF_500hPa"
                     "MJO_suite"
                     "MJO_teleconnection"
                     "convective_transition_diag"
                     "precip_diurnal_cycle"
                     "MJO_prop_amp"
                     )
# create the inputdata directory
input_dir="inputdata/test/obs_data"

if [[ ! -d "${input_dir}" ]]; then
  mkdir -p "${input_dir}"
fi

pushd ${input_dir}

## create directories for pod input data
for i in "${pod_names[@]}"
do
  if [[ ! -d "${i}" ]]; then
    echo "Creating directory ${i}"
    mkdir "${i}"
  fi
done

popd

echo "$(ls ${input_dir})"
