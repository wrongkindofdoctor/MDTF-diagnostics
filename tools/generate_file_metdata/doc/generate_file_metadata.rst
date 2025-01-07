.. _ref-generate-file-metadata:

generate_file_metadata.py
=====================

USAGE
-----
Generate netCDF or Zarr metadata json files for use with Kerchunk

To use, run the following command:

`> ./generate_file_metadata.py
--input_dir [input directory path]
--output_dir [output_directory_path]
--location [local | aws]`

Input
-----
  --input_dir (str, required): path to the input directory
  --output_dir (str, optional): path to the output directory that will contain the metadata json file. Defaults to
    the current working directory.
  --location (str, optional): local = local filesystem [default], aws = Amazon Web Services S3 cloud system

Output
------
Metadata data json file for each file in the input directory

Required packages:
------------------
The required packages are included in the _MDTF_base conda

- click
- fsspec
- kerchunk
- os
- sys
- ujson
