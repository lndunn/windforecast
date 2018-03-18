import pandas as pd
import numpy as np

import os
import sys

from datetime import datetime, timedelta


def getmetadata(lines):
	station = lines[1].strip()
	lat, lon, elev = [val.strip() for val in lines[3].split('   ')]
	datestr, utcoffset = [val.strip() for val in lines[4].split('   ')]

	metadata = {'station': station,
				'latitude': lat,
				'longitude': lon,
				'elevation': elev,
				'time': datetime.strptime(datestr.strip(), '%y %m %d %H %M %S'),
				'utcoffset': timedelta(minutes=int(utcoffset)),
				}

	return pd.DataFrame(metadata, index=[0,])

def getwindspeeds(lines):
	df = pd.DataFrame(columns=['altitude','windSpeed','windDir',])
	for i, line in enumerate(lines[11:-1]):
		df.loc[i] = [float(line[:7].strip()), float(line[7:16].strip()), float(line[16:25].strip()),]
	df[df==999999] = np.nan
	return df

def gettemperatures(lines):
	df = pd.DataFrame(columns=['altitude','temperature',])
	for i, line in enumerate(lines[11:-1]):
		df.loc[i] = [float(line[:7].strip()), float(line[7:16].strip()),]
	df[df==999999] = np.nan
	return df


def readfile(fname, datadir, parsefunc=None):
	fpath = os.path.join(datadir, fname)
	with open(fpath, 'r') as f:
		ftext = f.read()

	tables = ftext.split('$')

	metadata = []
	data = []

	for i, table in enumerate(tables):
		if len(table) < 20:
			continue

		rows = table.split('\r\n')

		meta = getmetadata(rows)
		meta['fname'] = fname
		meta['obs'] = i
		metadata.append(meta)

		df = parsefunc(rows)
		df['fname'] = fname
		df['obs'] = i
		df['time'] = meta['time'].ix[0]
		data.append(df)

	return metadata, data

def printprogress(n, milestones, starttime):
	if n in milestones:
		print '%i %% done. Time elapsed: %s'%(100*float(n)/milestones[-1], str(datetime.now()-starttime).split('.')[0])

def writetodisk(data, dest):
	for obstype in data.keys():
		for datatype in data[obstype].keys():
			if len(data[obstype][datatype])==0:
				continue
			destdir, destfname = os.path.split(dest)
			fname = os.path.join(destdir, ''.join([obstype, datatype, destfname]))
			
			if os.path.exists(fname):
				with open(fname, 'a') as f:
					pd.concat(data[obstype][datatype]).to_csv(f, index=False, header=False)
			else:
				pd.concat(data[obstype][datatype]).to_csv(fname, index=False, header=True)



def importdata(datadir, dest):

	data = {'W': {'metadata': [], 'data': []}, 'T': {'metadata': [], 'data': []}}
	files = os.listdir(datadir)
	nfiles = len(files)
	starttime = datetime.now()
	pctiles = (np.linspace(0,nfiles,101)[1:]).astype(int)

	for n, fname in enumerate(files):
		obstype = fname[0]
		if obstype=='W':
			func = getwindspeeds
		elif obstype=='T':
			func = gettemperatures
		_metadata, _data = readfile(fname, datadir, parsefunc=func)
		data[obstype]['metadata'].extend(_metadata)
		data[obstype]['data'].extend(_data)

		if n in pctiles:
			writetodisk(data, dest)
			printprogress(n, pctiles, starttime)
			data = {'W': {'metadata': [], 'data': []}, 'T': {'metadata': [], 'data': []}}

	return data


def mergedfs(data):
	winddata = pd.concat(data['W']['data'])
	tempdata = pd.concat(data['T']['data'])

	return winddata.merge(tempdata, on=['time','altitude'], how='outer', suffixes=('_wind','_temp'))

def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts


if __name__=='__main__':
	args = getopts(sys.argv)
	destdir = args['-o'] if '-o' in args.keys() else os.getcwd()
	destfname = args['-f'] if '-f' in args.keys() else '.csv'
	if '-i' not in args.keys():
		print 'You need to specify a path to the raw data'
		raise IOError()

	datadir = args['-i']

	print "reading data from '%s', writing to '%s/[filename]%s'"%(datadir, destdir, destfname)

	if not os.path.exists(destdir):
		os.mkdir(destdir)

	fname = os.path.join(destdir, ''.join(['W', 'data', destfname]))
	if not os.path.exists(os.path.join(destdir, fname)):
		pass
	else:
		print 'Output file by this name already exists. Append new data to existing file, or specify a new filename'
		ans = input('Append? [Y/n]? ')
		if ans == 'Y':
			pass
		else:
			ans = input('Specify new file name [or exit]: ')
			if ans == 'exit':
				assert False, 'if you say so'
			else:
				destfname = str(ans)

	data = importdata(datadir, os.path.join(destdir, destfname))