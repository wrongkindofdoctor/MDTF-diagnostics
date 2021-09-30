BootStrap: debootstrap
OSVersion: bionic
MirrorURL: http://us.archive.ubuntu.com/ubuntu/

Bootstrap: docker
From: continuumio/miniconda3
%runscript
    export CODE_ROOT="/proj/mdtf/MDTF-diagnostics"
    echo "Arguments received: $*"
    exec "${CODE_ROOT}"/mdtf "$@"
%labels
    Author 20195932+wrongkindofdoctor@users.noreply.github.com
    Version alpha-01
%help
   This is a singularity definitions file for the MDTF-diagnostics Package.
   Users should clone the MDTF-diagnostics repo to their machine as instructed
   in the documentation, then mount the following directories and files:
   src/default_tests.jsonc 
   MDTF-diagnostics/diagnostics
   the working directory ($WKDIR; ../wkdir by default)
   the input data directory (../inputdata by default)
   To build a singularity container called mdtf.sif from this definition file, run:
   $ cd ${MDTF_INSTALLDIR}/MDTF-diagnostics
   $ sudo singularity build mdtf.sif Singularity
   To run an interactive session in the mdtf.sif conatainer, run:
   $ singularity shell --bind ${MDTF_INSTALLDIR}/inputdata:/proj/mdtf/inputdata \
     --bind ${MDTF_INSTALLDIR}/wkdir:/proj/mdtf/wkdir \
     --bind ${MDTF_INSTALLDIR}/MDTF-diagnostics/diagnostics:/proj/mdtf/MDTF-diagnostics/diagnostics \
     --bind ${MDTF_INSTALLDIR}/MDTF-diagnostics/src/default_tests.jsonc:/proj/mdtf/MDTF-diagnostics/src/default_tests.jsonc
%post
   export CODE_ROOT="/proj/mdtf/MDTF-diagnostics"
   apt-get update && apt-get install -y git
# clean up
   apt-get clean
# test conda install
   chmod -R 775 "/opt/conda"
   conda info
# Install MDTF-diagnostics
# make mdtf directory
   mkdir -p "${CODE_ROOT}"
   ls "/proj"
   chmod -R 775 /proj/mdtf
   cd /proj/mdtf
   mkdir inputdata
   mkdir wkdir
   chmod -R 775 "${CODE_ROOT}"
   git clone https://github.com/NOAA-GFDL/MDTF-diagnostics.git
   ls "${CODE_ROOT}"
   cd "${CODE_ROOT}"
   git checkout develop
   ${CODE_ROOT}/src/conda/conda_env_setup.sh --all --conda_root /opt/conda --env_dir /opt/conda/envs
   # remove directories that will be user-mounted for modification
   rm -rf doc
   rm -rf diagnostics
   # make a new empty diagnostics directory for binding
   mkdir diagnostics
   # test the MDTF installation
   ${CODE_ROOT}/mdtf -h
