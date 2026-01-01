#!/usr/bin/env python
"""
Find exposures that haven't been ray traced.
"""
__author__ = "Alex Drlica-Wagner"

import glob
import numpy as np
import pylab as plt
import pandas as pd

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('outfile')
parser.add_argument('-f','--filename', help='list of exposures (instead of query)')
args = parser.parse_args()

# Excluded PROPIDs
PROPIDS = [
    '2012B-0001', #-- DES WIDE
    '2012B-0002', #-- DES SN
    '2012B-0003', #-- DES SV
    '2012B-0004', #-- DECAM SV SN
    '2012B-9996', #-- DES DC7
    '2012B-9997', #-- DECam Test
    '2012B-9998', #-- DECam Test
    '2012B-9999', #-- Commissioning
    '2013A-9999', #-- Engineering
    '2014A-9000'  #-- Standards
]

# SISPI query
QUERY = """
select e.expnum 
FROM exposure e, qa_summary q 
WHERE e.expnum = q.expnum
AND e.nite between 20121024 AND 20240201
AND e.band in ('g','r','i','z') and e.exptime >= 30
AND e.obstype = 'object'
AND q.t_eff > 0.1 and q.psf_fwhm < 2.0
AND e.propid NOT IN %s
AND e.expnum NOT BETWEEN 222736 AND 223265 -- quotes in object name
ORDER BY e.expnum
"""%(str(tuple(PROPIDS)))

if args.filename:
    print("Reading %s..."%args.filename)
    df = pd.read_csv(args.filename)
    df.columns = df.columns.str.upper()
    sel = ~np.in1d(df['PROPID'], PROPIDS)
    df = df.loc[sel]
else:
    import easyaccess as ea
    print("Querying DB...")
    print(QUERY)
    conn = ea.connect(section='decade')
    df = conn.query_to_pandas(QUERY)

# Add problematic exposures from Chin Yi
extra = pd.read_csv('data/problemetic_tiles_DR3_2_20240209.csv')
sel = (extra['score'] == 1) # bright stars
extra = extra[sel]
df = pd.concat([df,pd.DataFrame({'EXPNUM':extra['expnum']})], ignore_index=True)

done = []
for f in glob.glob('v*/survey-*.txt'):
    print(f)
    done.append(pd.read_csv(f,sep='\t')['expnum'].values)
done = np.unique(np.concatenate(done))

sel = ~np.in1d(df['EXPNUM'].values, done)
print("Selecting %s new exposures..."%sel.sum())

outfile = args.outfile
print("Writing %s..."%outfile)
df.loc[sel].to_csv(outfile, index=False)
