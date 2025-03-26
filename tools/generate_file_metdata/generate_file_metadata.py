# ======================================================================
# NOAA Model Diagnostics Task Force (MDTF)
# ======================================================================
# USAGE: Generate JSON metadata file for netCDF or Zarr files stored
# on a local file system or AWS s3 server
#
# Input:
# --input_dir: path to directory with input files
# --output_dir: path to the directory where reference json will be written
# --output file: name of the combined json file
# --file_system [local | s3]: type of system files are stored on
# --include vars: list of input variables to search for in the input_dir if you don't want metadata for all files
# Output: json file with metadata for files in the input_dir

import click
from kerchunk.combine import MultiZarrToZarr
from kerchunk.netCDF3 import NetCDF3ToZarr
import fsspec
import glob
import json
import os
import sys
from tempfile import TemporaryDirectory


fs_out_parms = dict(mode='rb', anon=True, default_fill_cache=False, default_cache_type='first')

def write_fsspec(input_file, output_dir):
    print(f"Running kerchunk generation for {input_file}...")
    result = NetCDF3ToZarr(input_file)
    file_name = os.path.basename(input_file)
    file_name = file_name.replace('.nc', '.json')
    out_file_name = output_dir + '/' + file_name
    if os.path.isfile(out_file_name):
        print(f'Deleting existing file in {output_dir}')
        os.remove(out_file_name)
    with open(out_file_name, "wb") as f:
        f.write(json.dumps(result.translate()).encode())
    f.close()
    print(f"Finished writing {out_file_name}")
    return out_file_name

class ConvertStrToList(click.Option):
    def type_cast_value(self, ctx, value) -> list:
        try:
            value = str(value)
            assert value.count('[') == 1 and value.count(']') == 1
            list_as_str = value.replace('"', "'").split('[')[1].split(']')[0]
            list_of_items = [item.strip().strip("'") for item in list_as_str.split(',')]
            return list_of_items
        except Exception:
            raise click.BadParameter(value)

@click.option("--input_dir",
              type=click.Path(),
              required=False,
              default = '/archive/Jacob.Mims/fre/FMS2024.02_OM5_20240819/CM4.5v01_om5b06_piC_noBLING_NB/gfdl.ncrc5-intel23-prod-openmp/pp/atmos_cmip/ts/6hr/5yr',
              help="Input directory with target subdirectories or files."
                   "Recursive search performed for .nc files in subdirectories."
              )
@click.option("--output_dir",
              type=click.Path(),
              required=False,
              default = '/net/jml/mdtf/', #default=lambda: os.getcwd(),
              show_default = '(Current Working Directory)',
              help="Directory where metadata file will be written"
              )
@click.option("-fout",
              "--output_file",
              type=click.STRING,
              required=False,
              default = 'combined',
              show_default = 'combined',
              help="Combined zarr json output file name"
              )
@click.option("-s",
              "--file_system",
              type=click.Choice(['local', 's3'], case_sensitive=False),
              required=False,
              default='local',
              help="System where input files are stored"
              )
@click.option('--include_vars',
              required=False,
              cls=ConvertStrToList,
              default=['sos', 'zos'],
              help="List of variables to search for in file names if you "
                   "do not want all files in the input directory"
              )


@click.command()
def run(input_dir: click.Path,
        output_dir: click.Path,
        output_file: click.Path,
        file_system,
        include_vars) -> int :
    config = dict({'input_dir': input_dir,
                   'output_dir': output_dir,
                   'output_file': output_file,
                   'system': file_system,
                   'include_vars': include_vars}
                  )
    for k, v in config.items():
        print(f'Config {k} : {v}')

    # Code adapted from: https://guide.cloudnativegeo.org/kerchunk/kerchunk-in-practice.html
    # Initiate fsspec filesystem for reading.
    dir_path = config['input_dir']
    if not dir_path.endswith('/'):
        dir_path += '/'
    # anon=True if dataset on AWS does not require users to be logged
    fs_read = fsspec.filesystem(config['system'])
    if config['system'] == 'local':
        file_paths = []
        if len(config['include_vars']) > 0:
            for var in config['include_vars']:
                dir_path += '**/*.' + var + '*.nc'
                glob_dir = glob.glob(dir_path, recursive=True)
                file_paths.extend(glob_dir)
        else:
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

    temp_dir = TemporaryDirectory(prefix=config['output_dir'])
    assert os.path.isdir(temp_dir.name), "{out_dir} is not a directory".format(out_dir=temp_dir)

    try:
        output_files = [write_fsspec(f, temp_dir.name) for f in file_paths]
        # combine individual references into single consolidated reference
        print('Calling MultiZarrToZarr')
        mzz = MultiZarrToZarr(
            output_files,
            remote_protocol=config['system'],
            remote_options={'anon': True},
            concat_dims=['time'],
            coo_map={'time': 'cf:time'},
            # inline_threshold=0 means don't store any raw data in the kerchunk reference file.
            inline_threshold=0
        )
        print("Calling multiZarrToZarr.translate()")
        multi_kerchunk = mzz.translate()

        print("Writing combined json file")
        output_file = os.path.join(config['output_dir'], config['output_file'] + '.json')
        with open(output_file, 'wb') as f:
            f.write(json.dumps(multi_kerchunk).encode())
        f.close()

    except Exception as exc:
        print(exc)
        temp_dir.cleanup()
        return 1
    return 0

if __name__ == '__main__':
    exit_code = run(prog_name='generate file metadata')
    sys.exit(exit_code)
