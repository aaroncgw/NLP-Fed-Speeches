''' Post Data Pull Workflow

At this point in the program we have pulled and processed both the Fed speeches and interest rate date.
FED SPEECHES
    The results of this process have been saved in a pickle file in the data subdirectory called
        'ts_cosine_sim.p'
        It contains a list with the following three variables [ts_cos_last, ts_cos_avg_n, ts_date]
            ts_cos_last     contains the cosine similarity of the last fed speech to the ones on the ts_date
            ts_cos_avg_n    contains the cos. sim of the last 50 speeches to the ones made on ts_date
            ts_date is      contains the date in a crappy np.datetime64 object

    os.chdir("..")
    pickle_out = open('../data/ts_cosine_sim', 'wb')
    pickle.dump([ts_cos_last, ts_cos_avg_n, ts_dates], pickle_out)
    pickle_out.close()

INTEREST RATE DATA
    The interest rate data has been pulled from quandl and pre-processed. The data sits in a file called 'interest_rate_data.p'


STEPS:
    1. Load up the interest rate data
    2. Split into train/test
    3. Convert into three datasets
        raw yields
        discrete forwards
        cont.comp forwards
    4. EDA on the data in the training + cv set
    5. build model pipeline
        -estimate parameters of the model over the training set
        -build CV update parameters/etc
    6. Compare the results

'''

# SOMEWHERE HERE WE SHOULD DO EDA ON THESE FOR THE PRESENTATION

''' Working on the Gaussian Model for the MVP on base level rates '''
def forecast_gaussian(X):
    ''' Mean zero interest rates we just take the change here '''
    fcst = 0
    return fcst

''' ARIMA MODEL ON BASE RATES
For now lets just look at the 10 year
'''

def build_ARIMA_model(X, ar, ma, diff_ord, target):

    model = pf.ARIMA(data=X, ar=4, ma=4, integ = diff_ord, target=target, family = pf.Normal())

    # Estimate the latent variables with a maximum likelihood estimation
    model.fit("MLE")
    #x.summary()
    pred = model.predict(h=1)
    last_rate = X['10 YR'][-1]
    this_shock = pred['Differenced 10 YR'].iloc[0]
    next_rate = last_rate + this_shock

    return next_rate

def update_cv_data(X_train, X_cv, i):

    temp = X_cv[0:i]
    frames = [X_train, temp]
    X_this_cv = pd.concat(frames)

    return X_this_cv

def create_cv_forecasts(X_train, X_cv, dict_params):
    cv_len = len(X_cv)
    forecasts = np.zeros(shape=[cv_len,1])
    ar = dict_params['ar']
    ma = dict_params['ma']
    diff_ord = dict_params['diff_ord']
    target = dict_params[target]
    for i in range(cv_len):
        print(i)
        this_X = update_cv_data(X_train, X_cv, i)
        forecasts[i] = build_ARIMA_model(this_X, ar, ma, diff_ord,
                            target, family = pf.Normal())
    return forecasts

def cross_validate_models(model_dict, X_train, X_cv):
    '''
    Building a overlaying function that handles the cross validation

    Will take as an input a dictionary that includes the model type
    and all of the hyper parameters of the model

    INPUTS:
        X_train -   the dataframe containing the training dataset
        X_cv -      the dataframe containing the cross_val dataset
        model_dicf  A dictionary containing the hyper parameters
                     of the model
            EX Arima
            model = { 'ar': 4, 'ma':4, 'integ':1,
                        'target':this_column,
                        'family':pf.Normal()}
    OUTPUTS

    # We want a list of dictionaries
    # Each dictionary will contain the following
    'model': a text explaination of the model
    'hyper_params': a dictionary of hyper parameters of the model
        hyper_params = {'Model': model.model_name,
                    'hyperparams': dict_params,
                    'forecast': forecasts
                    'target': '10 YR'}
    'predictions' - a set of predictions of the model (errors)
    'simulations' - a set of the simulations ??? (or is this in predictions)
'''
    # setting up the initial arima model
    model_list = []

    this_name = 'Normal ARIMA(1,1,1)'
    hyper_params= {'ar':1, 'ma': 1, "diff_ord": 1, 'target':'10 YR'}
    forecast = 0

    model_inputs = {'model_type': 'ARIMA'
                    'name': this_name,
                    'target_class': 'rates'
                    'hyper_params': hyper_params,
                    'foreacst': forecasts}

    model_list.append(model_inputs)

    
    forecasts = create_cv_forecasts(X_train, X_cv, dict_params)

#Load up interest rate data
import numpy as np
import pandas as pd
import pyflux as pf
import datetime as datetime
import matplotlib.pyplot as plt

import os
import pickle

os.chdir('..')
X = pickle.load(open("data/interest_rate_data", "rb" ) )
#df_FX = pickle.load( open( "data/FX_data", "rb" ) )
#df_FED = pickle.load( open( "data/all_fed_speeches", "rb" ) )

# cannot use train/test split on this because it is time series
total_obs = len(X)
train_int = int(round(total_obs*.7, 0))
cv_int = int(round(total_obs*.85, 0))

X_train = X[0:train_int]
X_cv = X[train_int:cv_int]
X_test = X[cv_int:]

dict_params = {'ar':1, 'ma': 1, "diff_ord": 1, 'target':'10 YR'}

'''
Need to include a dictionary that stores all of the results of the models
'''

dict_results = {'Model': model.model_name,
              'hyperparams': dict_params,
              'forecast': forecasts}

models = []

# Store relevant information in the models list