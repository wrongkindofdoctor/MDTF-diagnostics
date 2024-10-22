import numpy as np
import xarray as xr
import cftime
import zarr

month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def generate_data():
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
    time_attrs = {
        "name": "time",
        "long_name": "time",
        "axis": "T",
        "calendar_type": "noleap",
        "bounds": "time_bnds",
        "standard_name": "time",
        "description": "Temporal mean",
        "units": "days since 0001-01-01 00:00:00",
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

    temp = xr.DataArray(
            np.random.uniform(low=208.0, high=312.0, size=(len(plev19), len(lat), len(lon), len(time))),
            dims=("plev19", "lat", "lon", "time"),
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
    print(ds)


def write_zarr():
    pass


def read_zarr():
    pass


if __name__ == '__main__':
    generate_data()
