# -*- coding: utf-8 -*-
import sys
from random import randint

import dash
import dash_core_components as dcc
import dash_html_components as html
from coronadash.dash_components import Col, Row
from coronadash.conf.config import myapp
from coronadash.conf.config import mydash
import pandas as pd 
import datetime
from dash.dependencies import Input, Output 
#import dash_dangerously_set_inner_html
from collections import OrderedDict
import plotly.graph_objs as go
import random
import requests
from tornado import httpclient
from coronadash.dash_server import app
#
# Setup the embedded Dash App and create the actual dash layout, callbacks, etc.:
# see: _create_app()
# 

def _create_app_layout(*args, **kwargs):
    ''' 
        Creates the actual dash application and layout
        Just put any Dash layout in here.
        Documentation and examples: https://dash.plot.ly/

        The default route is: /dash which calls the handler/dash.py which creates the app
        and renders the pow_dash template.    
    '''

    import os
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "data/2019_ncov_data.csv"))
    df.columns = map(str.lower, df.columns)
    df["date"] = pd.to_datetime(df["date"])
    df["date1"]=pd.to_datetime(df["date"].dt.strftime('%m/%d/%Y'))
    df["state"]=df["province/state"]
    #add a new column that only contains the day
    df['day'] = df['date'].dt.day
    # same for the month
    df['month'] = df['date'].dt.month
    df1=df.groupby(["date1","country"]).agg({"confirmed":"sum"})
    #groupby day, month and aggregate the Confirmed as sum
    #df_confirmed_by_day = df.groupby(["Date"]).agg({"Confirmed": "sum"}) 
    #df = df_confirmed_by_day
    app.layout = html.Div([
        dcc.Graph(id='corona_graph'),
        dcc.Slider(
            id='day-slider',
            min=df['date1'].min(),
            max=df['date1'].max(),
            value=df['date1'].min(),
            marks={str(i): str(i) for i in df['date1'].unique()},
            step=None
        )
    ])


    @app.callback(
        Output('corona_graph', 'figure'),
        [Input('day-slider', 'value')])
    def update_figure(selected_day):
        filtered_df = df[df.date1 == selected_day]
        traces = []
        #for i in filtered_df["Province/State"].unique():
        #    df_by_continent = filtered_df[filtered_df['Province/State'] == i]
        #    traces.append(go.Bar(
        #        x=str(i),
        #        y=df_by_continent['Confirmed'],
        #        
        #    ))

        return {
            'data': [
                { 
                    "y" : list(filtered_df["confirmed"]),
                    "x" : list(filtered_df["state"]),
                    "type" : "bar"
                }
            ],
            'layout': {
                "title" : "Confirmed infections by Province/State and date" + str(selected_day)
            }
        }

    return app.layout


def dispatcher(request, index=True, **kwargs):
    '''
        Dispatch the Dash and Dash Ajax requests
    '''
    #kwargs["external_stylesheets"] = mydash["external_stylesheets"]
    #
    # only serve the base layout once. 
    # 
    if index:
        try:
            app.layout = _create_app_layout(**kwargs)
        except dash.exceptions.DuplicateCallbackOutput:
            pass
        
    params = {
        'data': request.body,
        'method': request.method,
        'content_type': request.headers.get('Content-type')
    }
    with app.server.test_request_context(request.path, **params):
        app.server.preprocess_request()
        try:
            response = app.server.full_dispatch_request()
        except Exception as e:
            response = app.server.make_response(app.server.handle_exception(e))
            print(70*"=")
            print("done dash dispatching")
            print(70*"=")

        response.direct_passthrough = False
        return response.get_data()