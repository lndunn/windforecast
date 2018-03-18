import pandas as pd
import numpy as np

import os

from datetime import datetime

def getmetadata(flines):
	flines = [line.split('\t') for lin in flines]
	station = flines[1][0].strip()
	lat, lon, elev = flines[3]
	datestr, utcoffset = flines[4]

	metadata = {'station': station,
				'latitude': lat,
				'longitude': lon,
				'elevation': elev,
				'time': datetime.strptime(datestr, '%y %m %d %H %M %s'),
				'utcoffset': timedelta(minutes=utcoffset),
				}

	return metadata

def getwindspeeds(lines):
	df = pd.DataFrame(columns=['altitude','windSpeed','windDir',])
	for i, line in enumerate(lines[11:]):
		row = line.split('\t')
		df.loc[i] = [float(row[0]), float(row[1]), float(row[2]),]
	df[df==999999] = np.nan
	return df

def gettemperatures(lines):
	df = pd.DataFrame(columns=['altitude','temperature',])
	for i, line in enumerate(lines[11:]):
		row = line.split('\t')
		df.loc[i] = [float(row[0]), float(row[2]),]
	df[df==999999] = np.nan
	return df


def readfile(fname, datadir, parsefunc=None):
	fpath = os.path.join(datadir, fname)
	with open(fpath, 'r') as f:
		ftext = f.read()

	tables = ftext.split('$')

	metadata = []
	data = []

	for table in tables:
		rows = table.split('\r\n')
		metadata.append(getmetadata(rows))
		data.append(parsefunc(rows))

	return metadata, data

def importdata(datadir):
	metadata = []
	dataframes = {'W': [], 'T': []}
	for f in os.listdir(datadir):
		if f[0]=='W':
			meta, data = readfile(fname, datadir, parsefunc=getwindspeeds)
		elif f[0]=='T':
			meta, data = readfile(fname, datadir, parsefunc=gettemperatures)

		for col in ['time','latitude','longitude']:
			data[col] = meta[col]

		dataframes[f[0]].append(data)

	return pd.merge(dataframes['W'], dataframes['T'], on=['latitude','longitude','time','height'])