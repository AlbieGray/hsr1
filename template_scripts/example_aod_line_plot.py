# -*- coding: utf-8 -*-

# import hsr1, and also numpy and pandas which are used for data processing
import numpy as np
import pandas as pd
import hsr1

# creates DBDriver object for the database where the data to be plotted is stored
database_location = "C:/Users/albie/work/Albiegray/databases/test_ts.db"
db = hsr1.DBDriver(database_location)

# loads all the columns required for this plot. pc_time_end_measurement is used for plotting,
# and all the other columns are used to calculate the aod
data = db.db_load.load(["pc_time_end_measurement", "global_spectrum", "diffuse_spectrum", "sza", "sed"])

# only the aod_microtops will be plotted
aod_type = "aod_microtops"

# calculates the aod_values that will be used for the plot. 
# this calculates aod at all wavelengths, but the desired wavelengths will be selected later
aod_data = hsr1.utils.HsrFunc.calc_aod_from_df(data)

# these are the wavelengths that will be plotted
wavelengths = np.array([380, 440, 500, 675, 870, 1020])

# filters for just the aod type that is being used, and converts the series of arrays into a 2d array
aod = np.stack(aod_data[aod_type].values)
# filters the wavelengths to only include the selected wavelengths.
# -300 because the wavelengths are from 300-1100, so the first in the array is 300nm
aod = aod[:, wavelengths-300]

# convert the array back into a dataframe, and add the time column
limited_df = pd.DataFrame(aod, columns=wavelengths.astype(str))
limited_df["pc_time_end_measurement"] = aod_data["pc_time_end_measurement"]

# calculates which readings have a clear sky and which are cloudy. uses the "wood" method by default
# calculate_clearsky_filter returns an array of 1s and 0s which can be used to filter an array or dataframe
clearsky_filter = hsr1.utils.HsrFunc.calculate_clearsky_filter(data)

# filter the aod and time values using the clearsky filter
# this will cause gaps in the index where values were skipped,
#   reset_index returns it to a normal increasing index
limited_df = limited_df.loc[clearsky_filter, :].reset_index(drop=True)


# creates a graph object
graph = hsr1.Graph(db)

# plots the graph
# sets rows=3, days_in_row=7 to put fewer days on each page, which shows each day
#   in more detail than putting a whole month on a page
graph.plot_daily_line(dataframe=limited_df, 
                      columns=wavelengths.astype(str),
                      rows=3, days_in_row=7,
                      title_prefix=aod_type+"\n")
