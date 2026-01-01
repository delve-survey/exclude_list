#!/usr/bin/env python
"""
Convert exclude files to single expnum,ccdnum list.

> python bin/make_exclude.py y*/*.txt -o delve_exclude_YYYYMMDD.fits
"""
__author__ = "Alex Drlica-Wagner"

import numpy as np
import pandas as pd
import fitsio

CCDNUMS = np.arange(1,63)
DTYPE = [('EXPNUM', '>i4'), ('CCDNUM','>i2'), ('REASON','S30'), ('ANALYST','S30')]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('filenames',nargs='+')
    parser.add_argument('-o','--outfile',default='exclude.csv')
    parser.add_argument('-a','--analyst', default='kadrlica')
    args = parser.parse_args()

    expnum,ccdnum,reason = [],[],[]
    for f in args.filenames:
        print("Reading %s..."%f)

        if 'problem' in f:
            # 'problem' files list expnum only
            df = pd.read_csv(f,sep=r'\s{2,}',engine='python',
                             names=['Nite','Exposure','Problem'],
                             comment='#')
            d = df.to_records(index=False)
            expnum.append(np.repeat(d['Exposure'],62))
            ccdnum.append(np.tile(CCDNUMS,len(d['Exposure'])))
            reason.append(np.repeat(d['Problem'],62))
        else:
            # Other files expected to have at least expnum,ccdnum
            # Other starts with #, so that makes things complicated...
            names = pd.read_csv(f,nrows=0,sep='\s+').columns.to_list()
            df = pd.read_csv(f,sep='\s+',comment='#',names=names)
            d = df.to_records(index=False)
            try:
                np.isnan(d['expnum'])
            except:
                print("Bad expnum in: %s"%f)
            expnum.append(d['expnum'])
            ccdnum.append(d['ccdnum'])
            if 'ghost-scatter' in f:
                reason.append(len(d)*['Ghost/Scatter'])     
            elif 'streak' in f:
                reason.append(len(d)*['Streak'])
            elif 'noise' in f:
                reason.append(len(d)*['Noise'])
            elif 'readout' in f:
                reason.append(len(d)*['Readout'])
            elif 'ccd' in f:
                reason.append(len(d)*['Bad CCD'])
            elif 'processing' in f:
                reason.append(len(d)*['Processing'])
            elif 'comet' in f:
                reason.append(len(d)*['Comet'])
            else:
                reason.append(len(d)*['Unknown'])

    expnum = np.concatenate(expnum).astype(int)
    ccdnum = np.concatenate(ccdnum).astype(int)
    reason = np.concatenate(reason)
    analyst = np.repeat(args.analyst, len(reason))

    data = np.rec.fromarrays([expnum,ccdnum,reason,analyst],dtype=DTYPE)
    print("Excluding %s CCDs..."%len(data))
    length = data['REASON'].dtype.itemsize
    for r,c in  zip(*np.unique(data['REASON'],return_counts=True)):
        print("  {0:{length}s}: {1:d}".format(r.decode(),c,length=length))
    
    print("Writing %s..."%args.outfile)
    if args.outfile.endswith('.csv'):
        pd.DataFrame(data).to_csv(args.outfile,index=False)
    elif args.outfile.endswith(('.fits','.fz')):
        fitsio.write(args.outfile,data,clobber=True)
    else:
        print("Unrecognized file extension: %s"%args.outfile)

    print("Done.")
