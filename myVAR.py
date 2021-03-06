# Import the necessary libraries
import pandas as pd
import numpy as np
import seaborn as sns
sns.set()
# import the KMeans clustering model from scikit-learn
import matplotlib.pyplot as plt

import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tools.eval_measures import rmse, aic
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller, acf, grangercausalitytests
from statsmodels.tsa.vector_ar.vecm import coint_johansen

class myVAR:
    def __init__(self,ts):
        self.ts=ts
    
    def __repr__(self):
        return 'my vector autoregression (VAR)'

    def ts_split(self,nobs):
        """train/test split: indicate number of observations 
        in the test split"""
        self.nobs=nobs
        self.ts_train= self.ts[0:-self.nobs]
        self.ts_test=self.ts[-self.nobs:]

    def get_diff(self,ts,order=2,verbose=False):
        """difference the time series with the given order."""
        self.ts_diff_order=order
        ts_diff=ts
        for i in range(1,order+1,1):
            nsVars=adfuller_test(ts_diff,verbose=verbose)
            nsCount=len(nsVars)
            if nsCount > 0:
                ts_diff= ts_diff.diff().dropna()
            else:
                ts_diff= ts_diff
            if verbose:
                print(nsVars)
        return ts_diff

    def get_inv_diff(self,ts_diff,order=2):
        """get real values by inverting the differences."""
        ts_train=self.ts_train
        ts_inv = ts_diff.copy()
        columns = ts_train.columns
        for col in columns: 
            if order ==2:       
                # Roll back 2nd Diff
                ts_inv[str(col)+'_d1'] = (ts_train[col].iloc[-1]-ts_train[col].iloc[-2]) + ts_inv[str(col)+'_d2'].cumsum()
            # Roll back 1st Diff
            ts_inv[str(col)] = ts_train[col].iloc[-1] + ts_inv[str(col)+'_d1'].cumsum()
        ts_inv=ts_inv.loc[:, (~(ts_inv.columns.str.contains('_d\d')))]
        # self.ts_inv=ts_inv
        return ts_inv

    def inspect_lag(self,maxlag=10):
        """inspect information criteria for different lag values until maxlag"""
        self.model = VAR(self.ts_train_diff)
        for i in range(1,maxlag+1,1):
            try:
                fit = self.model.fit(i)
                print(i, fit.info_criteria)
            except:
                print('ERROR: CANNOT FIT DURING LAG INSPECTION')
                pass

    def get_fit(self,p):
        """fit the VAR with the given lag"""
        self.model = VAR(self.ts_train_diff)
        self.p=p
        # self.fit=self.model.fit(self.p)
        return self.model.fit(self.p)

    def get_forecast_diff(self,steps,plot=True):
        """differenced forecast for input number of steps. With optional plot"""
        p=self.p
        nobs=self.nobs
        ts_train_diff=self.ts_train_diff
        fit=self.fit
        # Input data for forecasting
        forecast_input = ts_train_diff.values[-p:]

        # setting indices
        idx=ts_train_diff.index.values[-nobs:][0]
        # Get forecasted values with prediction intervals
        fc_mean,fc_lower,fc_upper = fit.forecast_interval(y=forecast_input, steps=steps)
        
        ts_fc_diff=pd.DataFrame(fc_mean, 
            index=range(idx+nobs,idx+nobs+steps,1), 
            columns=ts_train_diff.columns + f'_d{self.ts_diff_order}')
        ts_fc_lower_diff=pd.DataFrame(fc_lower, 
            index=range(idx+nobs,idx+nobs+steps,1), 
            columns=ts_train_diff.columns + f'_d{self.ts_diff_order}')
        ts_fc_upper_diff=pd.DataFrame(fc_upper, 
            index=range(idx+nobs,idx+nobs+steps,1), 
            columns=ts_train_diff.columns + f'_d{self.ts_diff_order}')

        if plot:
            fit.plot_forecast(steps);
        # self.ts_fc_diff=ts_fc_diff
        return ts_fc_diff,ts_fc_lower_diff,ts_fc_upper_diff

    def get_forecast_error(self,ts_forecast):
        """get a table with various forecast errors"""
        ts_test = self.ts_test
        result_test=pd.DataFrame(columns=ts_test.columns,index=['ME','MPE','MAE','MAPE','RMSE'])
        for col in ts_test.columns:
            test=ts_test[col]
            forecast=ts_forecast[col][:self.nobs]
            me_test = np.mean(forecast - test)             # ME
            mpe_test = np.mean((forecast - test)/test)   # MPE
            mae_test = np.mean(np.abs(forecast - test))    # MAE
            mape_test = np.mean(np.abs(forecast - test)/np.abs(test))  # MAPE
            rmse_test = np.sqrt(np.mean((forecast - test)**2))  # RMSE
            result_test[col]=[mpe_test,mape_test,me_test,mae_test,rmse_test]
        return result_test

    def granger_matrix(self, maxlag=1,test='ssr_chi2test', verbose=False):
        """granger's causality matrix"""  
        data=self.ts  
        variables=data.columns
        ts = pd.DataFrame(np.zeros((len(variables), len(variables))), columns=variables, index=variables)
        for c in ts.columns:
            for r in ts.index:
                test_result = grangercausalitytests(data[[r, c]], maxlag=maxlag, verbose=False)
                p_values = [round(test_result[i+1][0][test][1],4) for i in range(maxlag)]
                if verbose: print(f'Y = {r}, X = {c}, P Values = {p_values}')
                min_p_value = np.min(p_values)
                ts.loc[r, c] = min_p_value
        ts.columns = [var + '_x' for var in variables]
        ts.index = [var + '_y' for var in variables]
        return ts

    def cointegration_test(self, sig=0.05): 
        """cointegration test for default significance 0.05"""
        ts=self.ts
        out = coint_johansen(ts,-1,5)
        d = {'0.1':0, '0.05':1, '0.01':2}
        traces = out.lr1
        cvts = out.cvt[:, d[str(sig)]]
        # Summary
        print(f'Name::Test Stat > C({int(100*(1-sig))}%)=>Signif  \n', '--'*20)
        for col, trace, cvt in zip(ts.columns, traces, cvts):
            print(col, ':: ', round(trace,2), ">", cvt, ' =>  ' , 'Sig.' if trace > cvt  else 'Not sig.')

    def check_serial_correlation(self,plot=True):
        """check serial correlation for the fit (with visualization)"""
        ts=self.ts
        fit=self.fit
        out = durbin_watson(fit.resid)
        for col, val in zip(ts.columns, out):
            print(round(val, 2),col)
        if plot:
            plt.bar(ts.columns,[round(val,2) for col, val in zip(ts.columns, out)])

def adfuller_test(ts, signif=0.05, verbose=False):
    """ADFuller for stationarity test of given series"""
    nonStationaryVars=[]
    for name, series in ts.iteritems():
        r = adfuller(series, autolag='AIC')
        output = {'test_statistic':round(r[0], 4), 'pvalue':round(r[1], 4), 'n_lags':round(r[2], 4), 'n_obs':r[3]}
        p_value = output['pvalue'] 
        # add non-stationary var
        if p_value > signif:
            nonStationaryVars.append(name)

        # Print Summary
        if verbose:
            print(f'\nADF "{name}"', "\n", '-'*47)
            print(f' Significance Level    = {signif}')
            print(f' Test Statistic        = {output["test_statistic"]}')
            print(f' No. Lags Chosen       = {output["n_lags"]}')
            for key,val in r[4].items():
                print(f' Critical value {key} = {round(val, 3)}')
            if p_value > signif:
                print(f' Null Hypothesis: Data has unit root. Non-Stationary.')
                print(f" => P-Value = {p_value}. Weak evidence to reject the Null Hypothesis.")
                print(f" => Series is Non-Stationary. {len(nonStationaryVars)}")  
            else:
                print(f" => P-Value = {p_value}. Rejecting Null Hypothesis.")
                print(f" => Series is Stationary.")
    return nonStationaryVars

def plot_vars(ts):
    """plot the column time series for the given data"""
    fig, axes = plt.subplots(nrows=int(len(ts.columns)/2)+1, ncols=2, dpi=120, figsize=(10,6))
    for i, ax in enumerate(axes.flatten()):
        if i > len(ts.columns)-1:
            break
        data = ts[ts.columns[i]]
        ax.plot(data, color='red', linewidth=1)
        # Decorations
        ax.set_title(ts.columns[i])
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        ax.spines["top"].set_alpha(0)
        ax.tick_params(labelsize=6)
    plt.tight_layout();

def plot_comparison(obj,steps,name,figsize=(10,6),interval=True):
    """plot a comparison between two series"""
    data=obj.ts
    data_train=obj.ts_train
    results=obj.ts_results
    forecast=pd.concat([data_train[-1:],obj.ts_forecast[:steps]])
    if interval:
        forecast.lower=pd.concat([data_train[-1:],obj.ts_forecast.lower[:steps]])
        forecast.upper=pd.concat([data_train[-1:],obj.ts_forecast.upper[:steps]])
    fig, axes = plt.subplots(nrows=int(np.ceil(len(data.columns)/2)),ncols=2, dpi=150,figsize=figsize)
    for i, (col,ax) in enumerate(zip(data.columns, axes.flatten())):
        forecast[col].plot(legend=True, ax=ax,label='Forecast',linestyle='--',color='r').autoscale(axis='x',tight=True)
        data[col].plot(legend=True, ax=ax,label='Data');
        if interval:
            forecast.lower[col].plot(legend=True, ax=ax,label='95% Forecast Interval',linestyle=':',color='r').autoscale(axis='x',tight=True)
            forecast.upper[col].plot(legend=True, ax=ax,linestyle=':',color='r').autoscale(axis='x',tight=True)
            ax.fill_between(forecast[col].index, forecast.lower[col],forecast.upper[col], color='r', alpha=0.2,label='Forecast 95% interval')
        ax.set_title(col + ": Comparison")
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        ax.spines["top"].set_alpha(0)
        # ax.set_xlim([data.index[0],forecast.index[0]+steps])
        # ax.set_ylim([np.amin(results[col][0]),np.amax(results[col])])
    fig.suptitle(name)
    plt.tight_layout();
