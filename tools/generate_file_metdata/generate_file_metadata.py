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
import ujson


def gen_json_metadata_files(file_path: str, output_dir: str):
    """Generate json metadata files for each file on a local file system for use with kerchunk
    """
    so = dict(
        mode="rb", anon=True, default_fill_cache=False, default_cache_type="none"
    )
    with fsspec.open(file_path, **so) as inf:
        h5chunks = kerchunk.hdf.SingleHdf5ToZarr(inf, file_path, inline_threshold=300)
        with open(f"{output_dir}/{file_path.split('/')[-1]}.json", 'wb') as outf:
            outf.write(ujson.dumps(h5chunks.translate()).encode())

def main():
    pass

if __name__ == '__main__':
    main(prog_name='generate file metadata')