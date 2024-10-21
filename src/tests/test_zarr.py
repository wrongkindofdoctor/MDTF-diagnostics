import numpy as np
import xarray as xr
import cftime
import zarr


def generate_data():
    days = np.arange(15, 366, 30)
    time = [cftime.DatetimeNoLeap(*x, calendar="noleap") for x in (1, 0, [d for d in days])]
    time_attrs = {
        "name": "time",
        "long_name": "time",
        "axis": "T",
        "calendar_type": "noleap",
        "bounds": "time_bnds",
        "standard_name": "time",
        "description": "Temporal mean",
        "units": "days since 2004-01-01 00:00:00",
    }
    lat = np.arange(-89.5, 89.5, 2)
    lat_attrs = dict(name="lat",
                     type="geodetic",
                     units="degrees_north",
                     standard_name="latitude",
                     axis="Y")

    lon = np.arange(-180.0, 180.0, 2.5)
    lon_attrs = dict(name="lon",
                     prime_meridian="greenwich",
                     units="degrees_east",
                     standard_name="longitude",
                     axis="X")

    plev19 = np.array(
        [
            100000.0,
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

    temp = xr.DataArray(
            np.random.uniform(low=208.0, high=312.0, size=(12, 9, 144, 90)),
            dims=("plev19", "latitude", "longitude", "time"),
            coords={
                "plev19": plev19,
                "latitude": lat,
                "longitude": lon,
                "time": time
            },
            attrs={"name": "temp",
                   "standard_name": "air_temperature",
                   "units": "K",
                   "realm": "atmos"},
    )
    ds = xr.Dataset({"temp": temp},
                    coords={"plev19": (plev19,
                                       plev19_attrs
                                       ),
                            "latitude": (lat,
                                         lat_attrs
                                         ),
                            "longitude": (lon,
                                          lon_attrs
                                          ),
                            "time": (time,
                                     time_attrs
                                     )

                            },
                    attrs={"description": "Test dataset",
                           "convention": "cmip"}
                    )
    print(ds)


def write_zarr():
    pass


def read_zarr():
    pass


if __name__ == '__main__':
    generate_data()
