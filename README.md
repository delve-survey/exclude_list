# DECam Exclude Lists

Assemble lists of bad/suspect DECam images to exclude from high-level processing. These lists are collected using a number of techniques including an automated ray-tracing procedure and visual inspection. These lists follow the same format as the DES exclusion lists found [here](https://github.com/des-science/exclude_list).

## Execution

Create pngs of the problem exposures:
```bash
./bin/run_png.sh
```
Assemble the webpages:
```bash
./bin/run_www.sh
```
Compile the list of excluded CCD images (expnum/ccdnum) where `YYYYMMDD` is the current date:
```bash
python bin/make_exclude_list.py y*/*.txt -o delve_exclude_YYYYMMDD.fits
```

Upload list to the DESDM Oracle database:
```bash
easyaccess -s decade -lt delve_exclude_YYYYMMDD.fits
easyaccess -s decade -c "grant select on DELVE_EXCLUDE_YYYYMMDD to PUBLIC;"
```

## Usage

If you use this exposure list, please be sure to include a link to repository in your publication along with citations to DES ([DES Collaboration 2016](https://arxiv.org/abs/2101.05765)) and DELVE ([Drlica-Wagner et al. 2021](https://arxiv.org/abs/2103.07476)). Details on the automated ray-tracing technique used to identify ghosts and scattered light can be found in  [Kent (2013)](https://doi.org/10.2172/1690257) and is described in some detail in ([Chang et al. 2021](https://arxiv.org/abs/2105.10524)).
