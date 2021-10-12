# atmos
Atmospheric Model Output System v0.1

updated: 12 October 2021

The Atmospheric Model Output System (ATMOS) is a set of python scripts that will ultimately be able to read
various atmospheric model output types like WRF, RRFS, and HRRR and return a class with user defined dimensions, 
coordinates, and varialbes, like nx, ny, nz, and temperature.

Currently, there are two files both config.py and config_model_ouptput.py and WRF, RRFS, and HRRR model output
can be read, dims and coords can be set. 

An example for WRF model output is below:

```
from config_model_output import ModelOutput

main_dir = "/main_directory/still_main_directory/"
sub_dir = ""
valid_time = "2021-01-01_22:00:00" # Needs to match time format in config.py
domain = "d01"

# WRF instance of ModelOutput
wrf_sim1 = ModelOutput("WRF", "NETCDF", main_dir, sub_dir, valid_time, domain)

# Returns a list of valid files based on user input wrf_sim1.valid_files and wrf_sim1.unread_files
wrf_sim1.find_valid_files() 

# Reads valid files if data format is supported in config.py and removes from wrf_sim1.unread_files
wrf_sim1.read_file() 

# Sets dims as attributes using format in config.py (currently, nt, nz, ny, nx format)
# wrf_sim1.nz returns nz (for WRF this would be 'bottom_top')
wrf_sim1.check_for_attributes("dims) 

# Sets coords as attributes using format in config.py
# wrf_sim1.latitude returns a latitude array (for WRF this would be 'XLAT')
wrf_sim1.check_for_attributes("coords")
```
