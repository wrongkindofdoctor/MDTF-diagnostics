BootStrap: debootstrap
OSVersion: bionic
MirrorURL: http://us.archive.ubuntu.com/ubuntu/

Bootstrap: docker
From: continuumio/miniconda3
%test
    export CODE_ROOT="/opt/mdtf/MDTF-diagnostics"
    echo "TESTING, ATTENTION PLEASE."
    conda info
    "${CODE_ROOT}"/mdtf -h
%runscript
    export CODE_ROOT="/opt/mdtf/MDTF-diagnostics"
    echo "Arguments received: $*"
    exec "${CODE_ROOT}"/mdtf "$@"
%labels
    Author 20195932+wrongkindofdoctor@users.noreply.github.com
    Version alpha-01
%help
   This is a singularity definitions file for the MDTF-diagnostics Package.
   Users should clone the MDTF-diagnostics repo to their machine as instructed
   in the documentation, then mount the following directories:
   diagnostics
   src
%post
   export CODE_ROOT="/opt/mdtf/MDTF-diagnostics"
   apt-get update && apt-get install -y git
# clean up
   apt-get clean
# Install MDTF-diagnostics
# make mdtf directory
   mkdir -p "${CODE_ROOT}"
   ls "/opt"
   chmod -R 775 "${CODE_ROOT}"
   chmod -R 775 "/opt/conda"
   cd /opt/mdtf
   git clone https://github.com/wrongkindofdoctor/MDTF-diagnostics.git
   ls "${CODE_ROOT}"
   cd "${CODE_ROOT}"
   git checkout develop
   ls ./
   ${CODE_ROOT}/src/conda/conda_env_setup.sh --all --conda_root /opt/conda --env_dir /opt/conda/envs
