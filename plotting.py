import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib as mpl

import config

def conus_map(lon, lat, var, units = "",  
              map_west = -125, map_east = -70,  
              map_south = 20, map_north = 52):  
    """Very simple CONUS map with one variable plotted

        Parameters
            ----------
            lon : ndarray 
                2D longitude
            lat : ndarray
                2D latitude
            var : ndarray
                2D variable
            units : str
                variable units for colorbar
            map_west : int or float
                west most longitude (default -125)
            map_east : int or float
                east most longitude (default -70)
            map_south : int or float
                south most latitude (default 20)
            map_north : int or float
                north most latitude (default 52)
    """

    fig = plt.figure(figsize = (12, 12))
    ax = fig.add_subplot(
        1, 1, 1, projection = ccrs.LambertConformal())
    ax.set_extent(
        [map_west, map_east, map_south, map_north])

    # Cartopy features 
    # Land
    land_50m = cfeature.NaturalEarthFeature(
        'physical', 'land', '50m',
        edgecolor = 'black',
        facecolor = 'lightgray')

    # Ocean
    ocean_50m = cfeature.NaturalEarthFeature(
        'physical', 'ocean', '50m',
        edgecolor = 'face',
        facecolor = 'C0')

    # Lakes
    lakes_50m = cfeature.NaturalEarthFeature(
        'physical', 'lakes', '50m',
        edgecolor = 'black',
        facecolor = 'C0')
    
    # States
    states_50m = cfeature.NaturalEarthFeature(
        'cultural',
        'admin_1_states_provinces_lines',
        '50m', edgecolor = 'k',
        facecolor = 'none')

    # Countries
    c_50m = cfeature.NaturalEarthFeature(
        'cultural',
        'admin_0_countries',
        '50m',edgecolor = 'k',
        facecolor = 'none')
    
    ax.add_feature(land_50m, zorder = 1)
    ax.add_feature(ocean_50m, zorder = 2)
    ax.add_feature(lakes_50m, zorder = 3)
    ax.add_feature(c_50m, zorder = 3000)
    ax.add_feature(states_50m, zorder = 4000)        

    cmap = plt.get_cmap('jet')
    # Colorbar min is round to 10
    vmin = np.min(var) // 10 * 10

    # Colorbar max captures 99% of data
    # and is rounded to 10
    vmax = round(np.percentile(var, 99) / 10) * 10
    norm = mpl.colors.Normalize(vmin = vmin, vmax = vmax)

    # Plot
    p1 = ax.pcolormesh(lon, lat, var,
                       cmap = cmap, norm = norm, 
                       zorder = 9, transform = ccrs.PlateCarree())

    cbaxes = fig.add_axes([0.3, 0.25, .4, 0.01]) 
    cbar = fig.colorbar(p1, cax = cbaxes,
                        orientation = 'horizontal', aspect = 20, 
                        shrink = 0.5,
                        ticks = np.arange(
                            vmin, vmax+1, round((vmax-vmin)/10)))
    cbar.set_label("[" + units + "]")

    return fig
