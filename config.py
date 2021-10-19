# Supported models and data formats
# supported_models = ("wrf", "wrf-geogrid", "rrfs", "hrrr")
# supported_formats = ("netcdf", "grib2")

# Time format
time_format = {"wrf": "%Y-%m-%d_%H:%M:%S",
               "wrf-geogrid": None,
               "rrfs": "%Y%m%d%H",
               "hrrr": "%Y%m%d%H"
              }

# Model dimensions for supported models
dims = {"wrf": {"nt": "Time",
                "nz": "bottom_top",
                "ny": "south_north",
                "nx": "west_east"},
        "wrf-geogrid": {"nt": "Time",
                "ny": "south_north_stag",
                "nx": "west_east_stag"},
        "rrfs": {"nt": "time",
                 "nz": "pfull",
                 "nx": "grid_xt",
                 "ny": "grid_yt"},
        "hrrr": {"nz": "lv_HYBL0",
                 "ny": "ygrid_0",
                 "nx": "xgrid_0"}
        }

# Model cooordinates for supported models
coords = {"wrf": {"latitude": "XLAT",
                  "longitude": "XLONG",
                  "time": "XTIME"},
          "rrfs": {"xloc": "grid_xt",
                   "yloc": "grid_yt",
                   "pressure": "pfull",
                   "time": "time"},
          "hrrr": {"latitude": "gridlat_0",
                   "longitude": "gridlon_0"}
        }

supported_models = {
    'template': {
        # this key and it's children are optional
        'search_path_modification': {
            'use_domain': bool,
            'main_dir_sub_dir_div': '',
            'sub_dir_domain_div': '',
            'suffix': ''
        },
        # required but may be None
        'time_format': '%Y-%m-%d_%H:%M:%S',
    },
    'wrf': {
        'search_path_modification': {
            'use_domain': True,
            'main_dir_sub_dir_div': '',
            'sub_dir_file_div': '**/',
            'prefix': 'wrfout_',
            'suffix': '*'
        },
        'time_format': '%Y-%m-%d_%H:%M:%S',
        'time': 'XTIME',
        'dims': {
            'nt': 'Time',
            'nz': 'bottom_top',
            'ny': 'south_north',
            'nx': 'west_east'
        },
    },
    'wrf-geogrid': {
        'search_path_modification': {
            'use_domain': True,
            'main_dir_sub_dir_div': 'geo_em.',
            'suffix': '.nc'
        },
        'time_format': None,
    },
    'rrfs': {
        'search_path_modification': {
            'use_domain': False,
            'main_dir_sub_dir_div': '',
            'sub_dir_file_div': '**/',
            'prefix': 'dyn',
            'suffix': '*'
        },
        'time_format': '%Y%m%d%H',
    },
    'hrrr': {
        'search_path_modification': {
            'use_domain': False,
            'main_dir_sub_dir_div': '',
            'sub_dir_file_div': '**/',
            'prefix': 'hrrr.',
            'suffix': '*'
        },
        'time_format': '%Y%m%d%H',
    },
}
supported_formats = {
    'netcdf': {},
    'grib2': {},
}
