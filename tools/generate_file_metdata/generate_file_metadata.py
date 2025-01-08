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
import dask
from kerchunk.hdf import SingleHdf5ToZarr
import fsspec
import glob
import os
import sys
import json
import uuid
from dask.distributed import Client

def write_fsspec(fs_read, input_file, output_dir):
    with fs_read.open(input_file, **dict(mode="rb")) as infile:
        print(f"Running kerchunk generation for {input_file}...")
        # Chunks smaller than `inline_threshold` will be stored directly in the reference file as data (as opposed to a URL and byte range).
        file_name = os.path.basename(input_file)
        file_name = file_name.replace('.nc', '.json')
        out_file_name = output_dir + '/' + file_name
        if os.path.isfile(out_file_name):
            print(f'Deleting existing file in {output_dir}')
            os.remove(out_file_name)
        print(out_file_name)
        h5chunks = SingleHdf5ToZarr(infile, input_file, inline_threshold=300)
        with open(out_file_name, "wb") as f:
            f.write(json.dumps(h5chunks.translate()).encode())


@click.option('-i',
              '--input_dir',
              required=True,
              default='/archive/Jacob.Mims/fre/FMS2024.02_OM5_20240819/CM4.5v01_om5b06_piC_noBLING_NB/gfdl.ncrc5-intel23-prod-openmp/pp/atmos_cmip/ts/',
              type=click.Path(),
              help='Path to the directory with target files.'
                   ' Recursive search performed for .nc files in subdirectories.'
              )
@click.option("-o",
              "--output_dir",
              type=click.Path(),
              required=False,
              default = '/net/jml/mdtf/', #default=lambda: os.getcwd(),
              show_default = '(Current Working Directory)',
              help="Directory where metadata file will be written")
@click.option("-s",
              "--file_system",
              type=click.Choice(['local', 's3'], case_sensitive=False),
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
    dir_path = config['input_dir']
    if not dir_path.endswith('/'):
        dir_path += '/'
    # anon=True if dataset on AWS does not require users to be logged
    fs_read = fsspec.filesystem(config['system'], anon=True)
    if config['system'] == 'local':
        dir_path += '**/*.nc'
        file_paths = glob.glob(dir_path, recursive=True)
    else:
        dir_path = f"s3:/" + dir_path + '*.nc'
        # Retrieve list of available data
        file_paths = fs_read.glob(dir_path, recursive=True)
    if len(file_paths) > 0:
        print(f"{len(file_paths)} file(s) found in {dir_path}")
    else:
        print(f"No files found in {dir_path}")
        return 1

    out_dir = os.path.join(config['output_dir'], 'fsspec_refs')
    os.makedirs(out_dir, exist_ok=True)
    dask.compute(*[dask.delayed(write_fsspec)(fs_read, f, out_dir) for f in file_paths])
    return 0

if __name__ == '__main__':
    exit_code = run(prog_name='generate file metadata')
    sys.exit(exit_code)
