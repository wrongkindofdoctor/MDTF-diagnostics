#!/bin/bash -x
#SBATCH --job-name=test_am4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:30:00 # Time limit hrs:min:sec
#SBATCH --output=/contrib/${USER}/mdtf/CI_logs  # Standard output and error log

# install required software
sudo yum install -y debootstrap.noarch

# Allows fakeroot:
sudo sh -c 'echo user.max_user_namespaces=15000 \
    >/etc/sysctl.d/90-max_net_namespaces.conf'

sudo sysctl -p /etc/sysctl.d /etc/sysctl.d/90-max_net_namespaces.conf

sudo singularity config fakeroot --add ${USER}

export MDTF_ROOT=/contrib/${USER}/mdtf
# will probably need to modify /etc/singularity/singularity.conf BIND_PATH section instead to get this to work
export SINGULARITY_BINDPATH="${MDTF_ROOT}/inputdata:/proj/mdtf/inputdata, \
                        ${MDTF_ROOT}/wkdir:/proj/mdtf/wkdir, \
                        ${MDTF_ROOT}/MDTF-diagnostics/diagnostics:/proj/mdtf/MDTF-diagnostics/diagnostics, \
                        ${MDTF_ROOT}/MDTF-diagnostics/src/default_tests.jsonc:/proj/mdtf/MDTF-diagnostics/src/default_tests.jsonc "
cd ${MDTF_ROOT}/MDTF-diagnostics

sudo singularity run mdtf.sif -f /proj/mdtf/MDTF-diagnostics/src/default_tests.jsonc -v
