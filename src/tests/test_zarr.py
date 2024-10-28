import sys
import numpy as np
import xarray as xr
import cftime
import os
import zarr
import dask

month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def generate_data() -> xr.Dataset:
    # daily data from mdtf_test_data time
    nyears = 1
    startyear = 1
    months = list(np.arange(1, 13))
    days = [np.arange(1, month_days[n] + 1) for n, x in enumerate(months)]
    days = [item for sublist in days for item in sublist]
    days = days * nyears
    months = [[months[n]] * month_days[n] for n, x in enumerate(months)]
    months = [item for sublist in months for item in sublist]
    months = months * nyears
    years = list(np.arange(startyear, startyear + nyears))
    years = [[years[x]] * 365 for x in range(0, len(years))]
    years = [item for sublist in years for item in sublist]
    hours = [0] * len(days)
    time_tuple = list(zip(years, months, days, hours))

    time = [cftime.DatetimeNoLeap(*x, calendar="noleap") for x in time_tuple]
    # define time attributes
    time_attrs = {
        "name": "time",
        "long_name": "time",
        "axis": "T",
        "calendar_type": "noleap",
        "bounds": "time_bnds",
        "standard_name": "time",
        "description": "Temporal mean",
        "base_time_unit": "days since 0001-01-01 00:00:00",
    }
    # define latitude
    lat = np.arange(-89.5, 89.5, 2)
    lat_attrs = dict(name="lat",
                     type="geodetic",
                     units="degrees_north",
                     standard_name="latitude",
                     axis="Y")
    # define longitude
    lon = np.arange(-180.0, 180.0, 2.5)
    lon_attrs = dict(name="lon",
                     prime_meridian="greenwich",
                     units="degrees_east",
                     standard_name="longitude",
                     axis="X")
    # define atmospheric pressure levels
    plev19 = np.array(
           [100000.0,
            92500.0,
            85000.0,
            70000.0,
            60000.0,
            50000.0,
            40000.0,
            30000.0,
            25000.0,
            20000.0,
            15000.0,
            10000.0,
            7000.0,
            5000.0,
            3000.0,
            2000.0,
            1000.0,
            500.0,
            100.0,
            ]
    )
    plev19_attrs = dict(name="plev19",
                        standard_name="air_pressure",
                        units="Pa",
                        axis="Z",
                        positive="down")
    # define temperature array
    temp = xr.DataArray(
            np.random.uniform(low=208.0, high=312.0, size=(len(plev19), len(lat), len(lon), len(time))),
            dims=("plev19", "lat", "lon", "time"),
            attrs={"name": "temp",
                   "standard_name": "air_temperature",
                   "units": "K",
                   "realm": "atmos"}
    )
    precip = xr.DataArray(
        np.random.uniform(low=5.0e-12, high=1.0e-4, size=(len(lat), len(lon), len(time))),
        dims=("lat", "lon", "time"),
        attrs={"name": "precip",
               "standard_name": "precipitation_flux",
               "realm": "atmos",
               "units": "kg m-2 s-1"}
    )
    areacella = xr.DataArray(
        np.random.uniform(low=1.0, high=400, size=(len(lat), len(lon))),
        dims=("lat", "lon"),
        attrs={"name": "areacella",
               "standard_name": "cell_area",
               "realm": "atmos",
               "units": "m2"}
    )
    # instantiate dataset
    ds = xr.Dataset({
                     "temp": temp,
                     "precip": precip,
                     "areacella": areacella
                     },
                    coords={"plev19": ('plev19',
                                       plev19,
                                       plev19_attrs
                                       ),
                            "latitude": ('lat',
                                         lat,
                                         lat_attrs
                                         ),
                            "longitude": ('lon',
                                          lon,
                                          lon_attrs
                                          ),
                            "time": ('time',
                                     time,
                                     time_attrs
                                     )

                            },
                    attrs={"description": "Test dataset",
                           "convention": "cmip"}
                    )
    #print(ds)
    return ds

def write_zarr(ds: xr.Dataset) -> str:
    """Write an xarray dataset to a zarr file"""
    out_dir = os.getcwd()
    # Write metadata without computing array values
    data_store = os.path.join(out_dir, "test_metadata_zarr")
    #if os.path.isdir(data_store):
    #    print(f"removing existing data_store {data_store}")
    #    os.remove(data_store)
    ds.to_zarr(data_store, mode='w', compute=False)
    return data_store


def read_zarr(zarr_dir: str) -> xr.Dataset:
    ds_zarr = xr.open_zarr(zarr_dir)
    return ds_zarr



def append_to_zarr(zarr_dir: str, existing_ds: xr.Dataset):
    coord_names = [k for k in existing_ds.coords.sizes.keys()]
    dimsizes = [v for v in existing_ds.coords.sizes.values()]

    # define temperature array
    uwind = xr.DataArray(
        np.random.uniform(low=0, high=240, size=dimsizes),
        dims=coord_names,
        attrs={"name": "U",
               "standard_name": "eastward_wind",
               "units": "m s-1",
               "realm": "atmos"}
    )

    new_ds = xr.Dataset({"U": uwind})
    new_ds.to_zarr(zarr_dir, mode='a', compute=False)

def clean_up(zarr_dir: str):
    for dirpath, dirnames, filenames in os.walk(zarr_dir, topdown=False):
        delete_dir = os.path.join(zarr_dir, dirpath)
        for f in filenames:
            delete_path = os.path.join(dirpath, f)
            os.remove(delete_path)
        os.rmdir(delete_dir)
    if os.path.isdir(zarr_dir):
        print("Test directory cleanup failed")
        return 1
    return 0



if __name__ == '__main__':
    ds_write = generate_data()
    zarr_dir = write_zarr(ds_write)
    ds_read = read_zarr(zarr_dir)
    append_to_zarr(zarr_dir, ds_read)
    errno = clean_up(zarr_dir)
    sys.exit(errno)
