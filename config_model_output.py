import copy
import time
import glob
from datetime import datetime, timedelta

import numpy as np
import xarray as xr
import pandas as pd

import config
from config import supported_models as sm
from config import supported_formats as sf
from utils import get_logger


_LOGGER = get_logger('config_model_output', debug=True)


class ModelInputError(Exception):
    """Custom model input error"""
    pass


class ModelOutput:
    """A Python object used to read an format various atmospheric model output
    types
    """

    attr_type_enforcement = {
        'model_name': str,
        'data_format': str,
        'main_dir': str,
        'sub_dir': str,
        'valid_time': str,
        'domain': str,
    }

    def __init__(self, model_name, data_format, main_dir, sub_dir, valid_time, domain = 'd01'):
        """Sets model attributes from user input

        Parameters
            ----------
            model_name : str
                The model name, supported values in config.py and are currently
                `wrf`, `rrfs`, and `hrrr`
            data_format : str
                The model data type, supported values in config.py and
                currently `netcdf` and `grib2`
            main_dir : str
                The main model output directory
            sub_dir : str
                Subdirectories to be searched for model output.
                Can be a partial string, `**` will be appended
            valid_time : str
                Model output valid time
            domain : str
                domain to read, default is `d01` for wrf, but is unused for `rrfs` and `hrrr`

        Raises:
            TypeError
            ModelInputError
        """
        self.model_name = model_name
        self.data_format = data_format
        self.main_dir = main_dir
        self.sub_dir = sub_dir
        self.valid_time = valid_time
        self.domain = domain
        self._raise_for_invalid_parameter_types()
        self._clean_parameter_values()
        self._raise_for_invalid_parameter_values()
        self.config = sm[self.model_name]
        self.valid_files = None
        self.unread_files = None
        self.ds = None

    def _raise_for_invalid_parameter_types(self):
        """Checks attr types against class level attr/type map
        
        Raises:
            TypeError
        """
        for k, v in self.attr_type_enforcement.items():
            if not isinstance(getattr(self, k), v):
                raise TypeError(f"Input value '{k} = {getattr(self, k)}' must be a {v}")

    def _clean_parameter_values(self):
        """Performs basic transformations on attr values during __init__"""
        for k, v in self.attr_type_enforcement.items():
            # TODO: need to test this comparison
            if v is str:
                setattr(self, k, getattr(self, k).strip().lower())
        # Append appropriate endings to dir attrs if necessary
        if not self.main_dir.endswith("/"):
            self.main_dir += "/"

    def _raise_for_invalid_parameter_values(self):
        """Checks specific attr values to ensure they are valid per the config file.
        
        Raises:
            ModelInputError
        """
        # Check for supported models listed in config.py
        if self.model_name not in sm.keys():
            raise ModelInputError(
                f"Model name {self.model_name} is not supported. List of "
                f"supported model names: {sm.keys()}"
            )
        # Check for supported data formats
        if self.data_format not in sf.keys():
            raise ModelInputError(
                f"Data format {self.data_format} is not supported. List of"
                f"supported data formats: {sf.keys()}"
            )

    def __repr__(self):
        """Returns an unambiguous representation of the class instance"""
        return f"""<ModelOutput:
            model_name: {self.model_name},
            data_format: {self.data_format},
            main_dir: {self.main_dir},
            sub_dir: {self.sub_dir},
            valid_time: {self.valid_time},
            domain: {self.domain},
            valid_files: {self.valid_files},
            unread_files: {self.unread_files},
            ds: {str(self.ds)[:50]},
        >"""

    def __str__(self):
        """Returns a string of all users specified model attributes"""
        return f"""<ModelOutput: User defined attributes:
            model_name: {self.model_name},
            data_format: {self.data_format},
            main_dir: {self.main_dir},
            sub_dir: {self.sub_dir},
            valid_time: {self.valid_time},
            domain: {self.domain},
        >"""

    def set_valid_file_attrs(self, file_match):
        """Sets new attribute for valid files
           or appends to list of valid files

        Parameters
            ----------
            file_match : str
        """
        if getattr(self, "valid_files") is None:
            print(f"Valid file found: {file_match}")
            print(f"Setting attributes 'valid_files' "
                  f"and 'unread_files'")
            setattr(self, "valid_files", [file_match])
            setattr(self, "unread_files", [file_match])
        else:
            print(f"Additional valid file found: {file_match}, "
                  f"files in 'valid_files' sorted by forecast length")
            self.valid_files.append(file_match)
            self.unread_files.append(file_match)

    def find_valid_files(self):
        """Finds one or more valid files from user input of
            main_dir, sub_dir, and valid_time

        Raises:
            ModelInputError
        """
        # Search path
        search_path_attrs = self.config['search_path_modification']
        search_path = self.main_dir + search_path_attrs['main_dir_sub_dir_div'] \
                      + self.sub_dir + search_path_attrs['sub_dir_file_div'] \
                      + search_path_attrs['prefix']

        if search_path_attrs['use_domain']:
            search_path += self.domain
        search_path += search_path_attrs['suffix']

        # File search
        file_search = glob.glob(search_path)

        # Match if valid time in file search
        direct_file_match = [f for f in file_search if self.valid_time in f]

        # Simple case of single file matching valid_time
        if len(direct_file_match) == 1:
            self.set_valid_file_attrs(direct_file_match[0])
            return
        # Handles zero or more than one file matching the valid_time
        else:
            # The starting index of year, %Y, in format string
            year_index_start = self.config['time_format'].index("%Y")

            # Sorted list of all files that include the correct year: 'YYYY'
            # TODO: This will break if forecast spans two years
            all_files_matching_year = sorted(list(set(
                [f for f in file_search \
                 if self.valid_time[year_index_start:4] in f])))

            # Error if no files found
            if not all_files_matching_year:
                raise ModelInputError(f"File search returned "
                                      f"no matches, search path was "
                                      f"'{search_path}'\n"
                                      f"Check values of "
                                      f"'main_dir' = {self.main_dir}, \n"
                                      f"'sub_dir' = {self.sub_dir}, and "
                                      f"'valid_time' = {self.valid_time}")

            # Get location of 4-digit year in first matching file
            time_index_start = all_files_matching_year[0].rfind(
                self.valid_time[year_index_start:4])

            # Get file base time
            base_time_string = all_files_matching_year[0][
                time_index_start:time_index_start + len(self.valid_time)]

            # File format assumed to be everything after the last '/'
            file_format = [f[time_index_start:].rsplit("/")[1] \
                           for f in all_files_matching_year]

            # Get forecast and initialization hour from files
            forecast_hours = []
            init_hours = []
            for f in file_format:
                fhour = f.rfind("f")
                ihour = f.rfind("z")
                # The '4' is from the assumption that forecast hour
                # in file is 'f' followed by three or fewer numbers
                get_forecast_times = "".join([
                    c for c in f[fhour + 1: fhour + 4] if \
                    c.isdigit() and fhour > 0])
                # The '2' is from the assumption that initialization
                # time is two digits followed by 'z'
                get_init_times = "".join([
                    c for c in f[ihour - 2: ihour] if \
                    c.isdigit() and ihour > 0])
                forecast_hours.append(get_forecast_times)
                init_hours.append(get_init_times)

            # Files and initializations hours are sorted by forecast length
            files_sorted_by_forecast_hour = [
                x for _, x in sorted(zip(forecast_hours, all_files_matching_year))]
            init_hours_sorted_by_forecast_hour = [
                x for _, x in sorted(zip(forecast_hours, init_hours))]
            sorted_forecast_hours = sorted(forecast_hours)

            # Cases to handle base time + forecast
            # requires forecast_hours to exist
            if sorted_forecast_hours:
                # If initialization hours are found, add initialization 
                # hour and forecast and check against the hour in valid_time
                if all(init_hours_sorted_by_forecast_hour):
                    init_hour_plus_forecast = [
                        int(i) + int(f) for f, i in zip(
                            init_hours_sorted_by_forecast_hour, sorted_forecast_hours)]
                    # Replace %Y with YYYY to find the hour_index
                    hour_index_start = self.config['time_format'].replace('%Y', 'YYYY').index("%H")
                    # Valid hour is assumed to be 2 digits
                    find_valid_hour = int(self.valid_time[hour_index_start:hour_index_start + 2])
                    
                    for i, f in enumerate(init_hour_plus_forecast):
                        # If valid hour matches init + forecast,
                        # add that file to valid files, for example
                        # If valid hour = 20, init_hour = 12z and forecast = f008, 
                        # then init + forecast = 20 and file is sufficently matched
                        if f == find_valid_hour:
                            self.set_valid_file_attrs(
                                files_sorted_by_forecast_hour[i])
                        else:
                            print(f"'{f}' does not match "
                                  f"valid hour '{int(find_valid_hour)}'")
                else:
                    # This else deals with files that do not contain
                    # an initialization hour and are base time + forecast
                    # Base time in datetime (dt) format
                    base_time_dtformat = datetime.strptime(
                        base_time_string, self.config['time_format'])
                    # Calculation of base time + forecast
                    base_time_plus_forecast = [
                        datetime.strftime(base_time_dtformat \
                                          + timedelta(hours=int(i)), self.config['time_format']) \
                        for i in sorted(forecast_hours)]
                    # Search for base time + forecast in valid_time
                    base_time_plus_forecast_index = [
                        base_time_plus_forecast.index(f) \
                        for f in base_time_plus_forecast if f in self.valid_time]
                    if len(base_time_plus_forecast_index) == 1:
                        self.set_valid_file_attrs(all_files_matching_year[
                            base_time_plus_forecast_index[0]])
                    elif len(base_time_plus_forecast_index) == 0:
                        raise ModelInputError(f"Found no valid files from base time + forecast "
                                              f"with base time = {base_time_string} and \n"
                                              f"base time + forecast = {base_time_plus_forecast} "
                                              f"where valid time = {self.valid_time}")
                    else:
                        raise ModelInputError(f"Found multiple valid base time + forecast")
            else:
                # Error if no forecast hours are found
                raise ModelInputError(f"Forecast hours not found in file names "
                                      f"and are needed for base_time + forecast")

    def read_file(self):
        """Reads a single model output file using xarray

        Raises:
            IoError
        """
        if self.data_format == "netcdf":
            try:
                with xr.open_dataset(self.unread_files[0]) as ds:
                    print(f"Netcdf file read sucessfully: "
                          f"{self.unread_files[0]}")
                    self.ds = ds # Save the entire dataset as an attribute
                    self.unread_files.pop(0)
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
        elif self.data_format == "grib2":
            try:
                with xr.open_dataset(self.unread_files[0],
                                     engine='pynio') as ds:
                    print(f"Grib file read sucessfully: "
                          f"{self.unread_files[0]}")
                    self.ds = ds # Save the entire dataset as an attribute
                    self.unread_files.pop(0)
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))

    def check_for_attributes(self, tmpval="dims"):
        """Check for model attributes dims or coords set in
            config.py and sets if any are missing

        Parameters
            ----------
            tmpval : str
                Either `dims` or `coords`
        """
        if not (tmpval == "dims" or tmpval == "coords"):
            raise ModelInputError(f"Attribute check can only"
                                  f" be for 'dims' or 'coords',"
                                  f" not {tmpval}")

        print(f"Checking {self.model_name} attributes")
        if not self.model_name in getattr(config, tmpval):
            print(f"No {tmpval} for {self.model_name}")
            return

        # If attribute missing, get and set attribute
        if not all([hasattr(self, k) for k \
                    in getattr(config, tmpval)[self.model_name]]):
            [print(f"Missing {tmpval}: {k}") for k in getattr(
                config, tmpval)[self.model_name] if not hasattr(self, k)]
            self.get_model_attributes(tmpval)

    def get_model_attributes(self, tmpval):
        """Gets model attributes if missing

        Parameters
            ----------
            tmpval : str
                Either `dims` or `coords`
        """
        # For loop for simplicity since there are only 4 dimensions
        # max (time, x, y, z) and 4 coordinates max (time, x, y, z)
        for k,v in getattr(config, tmpval)[self.model_name].items():
            if not hasattr(self, k):
                tmpattr = getattr(self.ds, tmpval) \
                [getattr(config,tmpval)[self.model_name][k]]
                if hasattr(tmpattr, "values"):
                    print(f"Setting missing {tmpval} {k} to"
                          f"{type(tmpattr.values)}")
                    setattr(self, k, tmpattr.values)
                else:
                    print(f"Setting missing {tmpval} {k} to {tmpattr}")
                    setattr(self, k, tmpattr)
                    


