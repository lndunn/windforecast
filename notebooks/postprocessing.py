


def pivot(series, times, values):
    
    wdata = wdata.set_index(['altitude','time'], drop=False)
    tdata = tdata.set_index(['altitude','time'], drop=False)

    intervals, intervalMap = utils.mapIntervals(wdata.index.get_level_values('time'))
    windSpeed = pd.DataFrame(index=intervals, columns=wdata['altitude'].unique())
    temp = pd.DataFrame(index=intervals, columns=tdata['altitude'].unique())

    for h in windSpeed.keys():
        timeix = wdata.xs(h).index
        groups =  wdata.xs(h).groupby(intervalMap.loc[timeix].tolist())
        windSpeed[h] = groups['windSpeed'].sum()/groups['windSpeed'].count()

    windDir = pd.DataFrame(index=intervals, columns=wdata['altitude'].unique())
    for h in windSpeed.keys():
        timeix = wdata.xs(h).index
        groups =  wdata.xs(h).groupby(intervalMap.loc[timeix].tolist())
        windDir[h] = groups['windDir'].sum()/groups['windDir'].count()

    for h in temp.keys():
        timeix = tdata.xs(h).index
        groups =  tdata.xs(h).groupby(intervalMap.loc[timeix].tolist())
        temp[h] = groups['temperature'].sum()/groups['temperature'].count()