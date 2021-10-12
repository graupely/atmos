# atmos
Atmospheric Model Output System v0.1

updated: 12 October 2021

The Atmospheric Model Output System (ATMOS) is a set of python scripts that will ultimately be able to read
various atmospheric model output types like WRF, RRFS, and HRRR and return a class with user defined dimensions, 
coordinates, and varialbes, like nx, ny, nz, and temperature.

Currently, there are two files both config.py and config_model_ouptput.py

An example for WRF model output is below:

```
from config_model_output import ModelOutput

main_dir = "/main_directory/still_main_directory/"
sub_dir = ""
valid_time = "2021-01-01_22:00:00" # Needs to match time format in config.py
domain = "d01"

wrf_sim1 = ModelOutput("WRF", "NETCDF", main_dir, sub_dir, valid_time, domain)
wrf_sim1.find_valid_files() # Returns a list of valid files based on user input
wrf_sim1.read_file() # Reads valid files if data format is supported in config.py

# Sets dims as attributes using format in config.py (currently, nt, nz, ny, nx format)
# wrf_sim1.nz returns nz (for WRF this would be 'bottom_top')
wrf_sim1.check_for_attributes("dims) 

wrf_sim1.check_for_attributes("coords") # Set coordinates 
```
