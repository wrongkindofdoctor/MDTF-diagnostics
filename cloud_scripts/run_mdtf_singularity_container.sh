#!/bin/bash -x

# install required software
sudo yum install -y debootstrap.noarch

export MDTF_ROOT="/contrib/${USER}/mdtf"

# clean up the old working directory files
if [ -d "wkdir" ]; then
  printf '%s\n' "Removing wkdir directory"
  rm -rf "wkdir"
fi
mkdir wkdir
# define the bind paths in the singularity.conf file
sudo sed -i 's|\#bind path = /scratch|bind path = /contrib/Jessica.Liptak/mdtf/inputdata:/proj/mdtf/inputdata\nbind path = /contrib/Jessica.Liptak/mdtf/wkdir:/proj/mdtf/wkdir\nbind path = /contrib/Jessica.Liptak/mdtf/MDTF-diagnostics/diagnostics:/proj/mdtf/MDTF-diagnostics/diagnostics\nbind path = /contrib/Jessica.Liptak/mdtf/MDTF-diagnostics/tests/pw_gcp_test_set1.jsonc:/proj/mdtf/MDTF-diagnostics/src/default_tests.jsonc |g' \
   /etc/singularity/singularity.conf

# clone the MDTF-diagnostics repo
cd ${MDTF_ROOT}
if [ -d "MDTF-diagnostics" ]; then
  printf '%s\n' "Removing existing MDTF-diagnostics directory"
  rm -rf "MDTF-diagnostics"
fi
git clone -b add_docker_image https://github.com/wrongkindofdoctor/MDTF-diagnostics.git

# run the singularity container
sudo singularity run mdtf_diagnostics.sif -f /proj/mdtf/MDTF-diagnostics/src/default_tests.jsonc -v
