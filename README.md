# Python-Model-Cross-Section
Scripts that generate cross sections of temperature, wind, and relative humidity from the HRRR model.

You'll need to fetch your own data, found at https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/. The file(s) you'll be looking for take this format: hrrr.t{run hour}z.wrfnatf{frame hour}.grib2. {run hour} looks like 00 for 00z, and {frame hour} looks like 09 for the ninth hour in the run. These files are large, on the order of 700M per file.

There are other necessary tweaks to make the code run, such as changing file paths to match your setup and ensuring all libaries are installed in order for the script to run. There are plenty of caveats to be made, such as the wind cross section does not consider only in-plane or normal wind. Likewise, this code is written to create cross sections that appear linear in the HRRR's projected CRS. As such, the path may appear curved on a Mercator projection. If you have any questions, feel free to reach out to me on Twitter @EFisherWX. 
