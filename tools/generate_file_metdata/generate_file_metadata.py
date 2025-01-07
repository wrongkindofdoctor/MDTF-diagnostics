# ======================================================================
# NOAA Model Diagnostics Task Force (MDTF)
# ======================================================================
# USAGE: Generate JSON metadata file for netCDF or Zarr files stored
# on a local file system or AWS s3 server
#
# Input:
# --input_dir: path to directory with input files
# --output_dir: path to the directory where reference json will be written
# --file_system [local | aws]: type of system files are stored on
# Output: json file with metadata for files in the input_dir

import click
import kerchunk
import fsspec
import os
import sys


@click.option('-i',
              '--input_dir',
              required=True,
              default='/archive/Jacob.Mims/fre/FMS2024.02_OM5_20240819/CM4.5v01_om5b06_piC_noBLING_NB/gfdl.ncrc5-intel23-prod-openmp/pp/atmos_cmip/ts/',
              type=click.Path(),
              help='Path to the directory with target files. Can include wildcards (*)'
              )
@click.option("-o",
              "--output_dir",
              type=click.Path(),
              required=False,
              default=lambda: os.getcwd(),
              show_default = '(Current Working Directory)',
              help="Directory where metadata file will be written")
@click.option("-s",
              "--file_system",
              type=click.Choice(['local', 'aws'], case_sensitive=False),
              required=False,
              default='local',
              help="Type of system files are stored on")
@click.command()
def run(input_dir: click.Path, output_dir: click.Path, file_system) -> int :
    config = dict({'input_dir': input_dir,
                   'output_dir': output_dir,
                   'system': file_system}
                  )
    for k, v in config.items():
        print(f'Config {k} : {v}')

    # Code adapted from: https://guide.cloudnativegeo.org/kerchunk/kerchunk-in-practice.html
    # Initiate fsspec filesystem for reading.
    if config['system'] == 'local':
        fs_read = fsspec.filesystem("local")
        dir_path = config['input_dir']

    else:
        # set anon=True if dataset on AWS does not require users to be logged in to access.
        fs_read = fsspec.filesystem("s3", anon=True)
        dir_path = f"s3:/" + input_dir
    # Retrieve list of available data.
    if '*' not in dir_path:
        if dir_path.endswith('/'):
            dir_path += '*'
        else:
            dir_path += '/*'
    file_paths = fs_read.glob(dir_path)
    if len(file_paths) > 0:
        print(f"{len(file_paths)} file(s) found in {dir_path}")
    else:
        dir_path += '/*'
        file_paths = fs_read.glob(dir_path)
        if len(file_paths) == 0:
            print(f"No files found in {dir_path}")
            sys.exit(1)


if __name__ == '__main__':
    exit_code = run(prog_name='generate file metadata')
    sys.exit(exit_code)
