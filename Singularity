BootStrap: debootstrap
OSVersion: bionic
MirrorURL: http://us.archive.ubuntu.com/ubuntu/

%environment
    export CODE_ROOT="/opt/mdtf/MDTF-diagnostics"
%setup
    export CODE_ROOT="/opt/mdtf/MDTF-diagnostics"
# make mdtf directory
    if [[ ! -d "${CODE_ROOT}" ]]
    then
       mkdir -p "${CODE_ROOT}"
    fi
    ls "${CODE_ROOT}"
%files
    src ${CODE_ROOT}/src
    data ${CODE_ROOT}/data
    shared ${CODE_ROOT}/shared
    sites ${CODE_ROOT}/sites
    tests ${CODE_ROOT}/tests
    mdtf_framework.py "${CODE_ROOT}"/mdtf_framework.py
%test
    echo "TESTING, ATTENTION PLEASE."
    conda info
    "${CODE_ROOT}"/mdtf -h
%runscript
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
   apt-get update && apt-get install -y wget
# Get Miniconda3 installation script
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
# Change permission to execute build script
   chmod +x Miniconda3-latest-Linux-x86_64.sh
# install Miniconda3 and mamba package
   bash ./Miniconda3-latest-Linux-x86_64.sh -bfp /usr/local
   conda init bash
   conda install -c conda-forge mamba
# clean up
   apt-get clean
   rm -f Miniconda3-latest-Linux-x86_64.sh
# Install MDTF environments and generate wrapper script
   echo "Building MDTF-diagnostics wrapper and Conda environments"
   cd "${CODE_ROOT}"
   ls ./
   ./src/conda/conda_env_setup.sh --all --conda_root /usr/local/miniconda3 --env_dir /usr/local/miniconda3/envs
