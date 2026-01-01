#!/usr/bin/env python
"""
Download exposures for each year.
"""
__author__ = "Alex Drlica-Wagner"
from collections import OrderedDict as odict
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

SISPI_QUERY = """
SELECT TO_CHAR(date-'12 hours'::INTERVAL,'YYYYMMDD')::INT AS "#nite", 
       id AS expnum, 
       telra AS ra, 
       teldec AS dec, 
       filter AS fil, 
       exptime AS exp, 
       '{'||substring(object, 0, 21)||'}' AS object,
       airmass AS secz, 
       TO_CHAR(TO_TIMESTAMP(utc_dark),'HH:MM') AS ut, 
       'good' as status
FROM exposure
WHERE 
TO_CHAR(date-'12 hours'::INTERVAL,'YYYYMMDD')::INT between %(start)s AND %(end)s
AND filter in ('g','r','i','z') and exptime >= 30
AND flavor = 'object' AND discard = False 
-- AND delivered = True -- this doesn't seem necessary
AND propid NOT IN (
    --'2012B-0001', -- DES WIDE
    '2012B-0002', -- DES SN
    '2012B-0003', -- DES SV
    '2012B-0004', -- DECAM SV SN
    '2012B-9996', -- DES DC7
    '2012B-9997', -- DECam Test
    '2012B-9998', -- DECam Test
    '2012B-9999', -- Commissioning
    '2013A-9999', -- Engineering
    '2014A-9000'  -- Standards
)
AND id NOT BETWEEN 222736 AND 223265 -- quotes in object name
ORDER BY id
--LIMIT 10000
"""

DELVE_QUERY = """
SELECT e.nite AS "#nite", 
       e.expnum, 
       e.radeg AS ra, 
       e.decdeg AS dec, 
       e.band AS fil, 
       e.exptime AS exp, 
       '{'||substring(e.object, 0, 21)||'}' AS object,
       e.airmass AS secz, 
       TO_CHAR(date_obs,'HH:MM') AS ut, 
       'good' as status
FROM exposure e, qa_summary q
WHERE 
e.expnum = q.expnum
AND e.nite between %(start)s AND %(end)s
AND e.band in ('g','r','i','z') and e.exptime >= 30
AND abs(e.glat) > 9 AND e.obstype = 'object'
AND q.t_eff > 0.1 and q.psf_fwhm < 2.0
AND e.propid NOT IN (
    '2012B-0001', -- DES WIDE
    '2012B-0002', -- DES SN
    '2012B-0003', -- DES SV
    '2012B-0004', -- DECAM SV SN
    '2012B-9996', -- DES DC7
    '2012B-9997', -- DECam Test
    '2012B-9998', -- DECam Test
    '2012B-9999', -- Commissioning
    '2013A-9999', -- Engineering
    '2014A-9000'  -- Standards
)
AND e.expnum NOT BETWEEN 222736 AND 223265 -- quotes in object name
ORDER BY e.expnum
--LIMIT 10000
"""

DECADE_QUERY = """
SELECT e.nite AS "#nite", 
       e.expnum, 
       e.radeg AS ra, 
       e.decdeg AS dec, 
       e.band AS fil, 
       e.exptime AS exp, 
       '{'||substr(e.object, 0, 21)||'}' AS object,
       e.airmass AS secz, 
       SUBSTR(date_obs,12,5) AS ut, 
       'good' as status
FROM exposure e, qa_summary q
WHERE 
e.expnum = q.expnum
AND e.nite between %(start)s AND %(end)s
AND e.band in ('g','r','i','z') and e.exptime >= 30
AND e.obstype = 'object'
AND q.t_eff > 0.1 and q.psf_fwhm < 2.0
AND e.propid NOT IN (
    '2012B-0001', -- DES WIDE
    '2012B-0002', -- DES SN
    '2012B-0003', -- DES SV
    '2012B-0004', -- DECAM SV SN
    '2012B-9996', -- DES DC7
    '2012B-9997', -- DECam Test
    '2012B-9998', -- DECam Test
    '2012B-9999', -- Commissioning
    '2013A-9999', -- Engineering
    '2014A-9000'  -- Standards
)
AND e.expnum NOT BETWEEN 222736 AND 223265 -- quotes in object name
ORDER BY e.expnum
--LIMIT 10000
"""


# NOTE: The name of the output file needs to be "y[0-9]+" where [0-9]+
# is one or more integers (see decam/shutter.tcl).  If year is 'y0' or
# 'y1', the ray tracing will try to run scattered light (which we
# usually don't want). This should be used for exposures taken before
# 2014-03-14

YEARS = odict([
    (0, [20121024,20130801]), 
    (1, [20130801,20140314]), 
    (2, [20140314,20150801]),
    (3, [20150801,20160801]),
    (4, [20160801,20170801]),
    (5, [20170801,20180801]),
    (6, [20180801,20190801]),
    (7, [20190801,20200801]),
    (8, [20200801,20210801]),
    #(9, [20210801,20230101]),
    #(9, [20210801,20230731]),
    (9, [20210801,20220801]),
    (10,[20220801,20230801]),
    (11,[20230801,20240801]),
    (12,[20240801,20250801]),
])    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-y', '--year', default=None, type=int,
                        help='year to query')
    parser.add_argument('--db', default='sispi',
                        help='database for query')
    parser.add_argument('--explist', default=None,
                        help='exposure list to select from')
    args = parser.parse_args()

    if args.db.lower() in ('sispi'):
        print("SISI query...")
        conn = 'postgresql://decam_reader@des61.fnal.gov:5443/decam_prd'
        QUERY = SISPI_QUERY
        def run_query(query, conn):
            engine = create_engine(conn)
            return pd.read_sql_query(query,con=engine)
    elif args.db.lower() in ('delve','bliss'):
        print("DELVE query...")
        conn = 'postgresql://des_reader@des51.fnal.gov:5432/BLISS'
        QUERY = DELVE_QUERY
        def run_query(query, conn):
            engine = create_engine(conn)
            return pd.read_sql_query(query,con=engine)
    elif args.db.lower() in ('decade'):
        print("DECADE query...")
        import easyaccess as ea
        conn = ea.connect(section='decade')
        QUERY = DECADE_QUERY
        def run_query(query, conn):
            df = conn.query_to_pandas(query)
            return df
    elif args.db.endswith(('.csv','.csv.gz')):
        print("Loading from file: %s..."%args.db)
        conn = filename = args.db
        QUERY = """%(start)s, %(end)s"""
        def run_query(query, conn):
            start,end = [int(q) for q in query.split(',')]
            df = pd.read_csv(conn)
            sel = (df['nite'] >= start) & (df['nite'] <= end)
            column_mapping = {"nite": "#nite", "band": "fil", "exptime": "exp"}
            out = df.loc[sel][['nite','expnum','ra','dec','band','exptime']]
            out.rename(columns=column_mapping, inplace=True)
            out['object'] = 'object'
            out['secz'] = 1.0
            out['ut'] = '00:00'
            out['status'] = 'good'
            return out
    else:
        msg = 'Unrecognized database: %s'%args.db
        raise Exception(msg)

    #engine = create_engine(conn)

    for year,(start,end) in YEARS.items():
        print("Querying year {}...".format(year))
        if (args.year is not None) and (year != args.year): 
            print("Skipping year {}...".format(year))
            continue
            
        query = QUERY%dict(start=start,end=end)
        #df = pd.read_sql_query(query,con=engine)
        df = run_query(query,conn)
        df.columns = df.columns.str.lower()

        if args.explist:
            # Only select exposures in the explist
            explist = pd.read_csv(args.explist)
            explist.columns= explist.columns.str.lower()
            df = df[np.in1d(df['expnum'],explist['expnum'])]

        print("... {} exposures in output file.".format(len(df)))
        if not len(df): 
            continue

        outfile = 'survey-y{}.txt'.format(year)
        print("Writing {}...".format(outfile))
        df.to_csv(outfile,index=False,sep='\t')
