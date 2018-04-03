from modules import *

def mapIntervals(times, freq='30min'):
    start = times.min()
    start = datetime(start.year, start.month, start.day, start.hour)

    times = times.unique()
    intervals = pd.date_range(start=start, end=times.max(), freq=freq)

    intervalMap = pd.Series([intervals[intervals<t].max() for t in times], index=times)
    return intervals, intervalMap
    

def pivot(df, varname=None, to_rows=None, to_cols=None, 
        rownames=None, colnames=None, groups=None):

    df = df.set_index([to_cols,to_rows], drop=False)
    
    if type(rownames)==type(None):
        rownames=df[to_rows].unique()
    if type(colnames)==type(None):
        colnames= df[to_cols].unique()
    
    newdf = pd.DataFrame(index=rownames, columns=colnames)
    
    for col in newdf.keys():
        rowix = df.xs(col).index
        grouped = df.xs(col).groupby(groups.loc[rowix].tolist())
        newdf[col] = grouped[varname].sum()/grouped[varname].count()
    return newdf