BootStrap: debootstrap
OSVersion: bionic
MirrorURL: http://us.archive.ubuntu.com/ubuntu/

%environment
    export CODE_ROOT="/opt/mdtf/MDTF-diagnostics"
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
   export PATH="/usr/local/miniconda3/bin:$PATH"
   conda install -c conda-forge mamba
# clean up
   apt-get clean
   rm -f Miniconda3-latest-Linux-x86_64.sh
# Install MDTF-diagnostics
   echo "Building MDTF-diagnostics wrapper and Conda environments"
# Make mdtf directory
   if [[ ! -d "${CODE_ROOT}" ]]
   then
       mkdir -p "${CODE_ROOT}"
   fi
   ls /opt/mdtf
   echo "Building MDTF-diagnostics wrapper and Conda environments"
   cd /opt/mdtf
   git clone https://github.com/wrongkindofdoctor/MDTF-diagnostics.git
   ls "${CODE_ROOT}"
   cd "${CODE_ROOT}"
   git checkout develop
   ls ./
   ${CODE_ROOT}/src/conda/conda_env_setup.sh --all --conda_root /opt/miniconda3 --env_dir /opt/miniconda3/envs
