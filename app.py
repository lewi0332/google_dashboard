from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dash import Dash, no_update
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
import dash_auth
from dash.dependencies import Input, Output
from flask import Flask
import fohr_theme_light
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go
from tables import bonus_col, bonus_cell_cond, bonus_data_cond

CELL_PADDING = 15
DATA_PADDING = 15
TABLE_PADDING = 100
FONTSIZE = 12


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
RANGE_NAME = os.environ['RANGE_NAME']


def get_google_sheet():
    """
    Returns all values from the target google sheet.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        return values


def gsheet2df(gsheet):
    """ Converts Google sheet data to a Pandas DataFrame.
    Note: This script assumes that your data contains a header file on the first row!
    Also note that the Google API returns 'none' from empty cells.
    """
    header = gsheet[0]   # Assumes first line is header!
    values = gsheet[1:]  # Everything else is data.
    if not values:
        print('No data found.')
    else:
        df = pd.DataFrame(columns=header, data=values)
    return df


server = Flask(__name__)
PASS_ = os.environ['VALID_USERNAME_PASSWORD_PAIRS']
VALID_USERNAME_PASSWORD_PAIRS = {'demo': PASS_}


app = Dash(name=__name__,
           server=server,
           external_stylesheets=[dbc.themes.GRID])

app.config.suppress_callback_exceptions = False
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

app.layout = html.Div(
    html.Div([
        dbc.Row(
            dbc.Col([
                html.Img(id="swordmark",
                         src="./assets/specialized-wordmark-black-cmyk.jpg",
                         alt="Specialized Wordmark logo",
                         style={
                             'width': '60%',
                            #  'height': '30%'
                         }),
            ],  width={"size": 6, "offest": 1}), justify="left"
        ),
        dcc.Markdown("""
                # **_S-WORKS_** Stoke-o-Meter
                """,
                     style={
                         'font-family': 'plain light',
                         'color': 'Black',
                         'font-weight': 'light'
                     }),
        dcc.Markdown("""
                ---
                """,
                     style={
                         'font-family': 'plain light',
                         'color': 'grey',
                         'font-weight': 'light'
                     }),
        html.Br(),
        html.Label('Date Range',
                   style={
                       'font-family': 'plain',
                       'font-weight': 'light'
                   }),
        html.Br(),
        html.Br(),
        dcc.DatePickerRange(id='dt-picker-range',
                            start_date=datetime.now() - timedelta(days=90),
                            end_date=datetime.now()),
        html.Br(),
        dbc.Row([
                dbc.Col(
                    html.H2('Total Butts on Bikes',
                            style={
                                'font-family': 'plain',
                                'font-weight': 'light',
                                'color': 'grey',
                                'text-align': 'center',
                                'font-size': 24,
                                # 'width': 100
                            }),
                    align="center", width=3),
                dbc.Col(
                    html.H2('Total Activations:',
                            style={
                                'font-family': 'plain',
                                'font-weight': 'light',
                                'color': 'grey',
                                'font-size': 24,
                                'textAlign': 'center'

                            }),
                    align="center", width=3),
                dbc.Col(
                    html.H2('Total Staff Educated:',
                            style={
                                'font-family': 'plain',
                                'font-weight': 'light',
                                'color': 'grey',
                                'font-size': 24,
                                'text-align': 'center'
                            }),
                    align="center", width=3),
                ], justify='center', align='center', style={'padding-top': 80}),
        dbc.Row([
                dbc.Col(
                    html.H1(id='label_total_bob',
                               style={
                                   'font-family': 'plain light',
                                   'font-weight': 'light',
                                   'font-size': 36,
                                   'padding': 0,
                                   'textAlign': 'center'
                               }), align="center", width=3),
                dbc.Col(
                    html.H1(id='label_total_activations',
                               style={
                                   'font-family': 'plain light',
                                   'font-weight': 'light',
                                   'font-size': 36,
                                   'padding': 0,
                                   'textAlign': 'center'
                               }), align="center", width=3),
                dbc.Col(
                    html.H1(id='label_total_staff',
                               style={
                                   'font-family': 'plain light',
                                   'font-weight': 'light',
                                   'font-size': 36,
                                   'padding': 0,
                                   'textAlign': 'center'
                               }), align="center", width=3),
                ], justify='center'),
        html.Br(),
        dbc.Row([
                dbc.Col([
                    dcc.Graph(id='main_map', style={'height': '800px'})
                ])
                ]),
        html.Br(),
        html.Br(),
        dcc.Markdown("""
                # Filtered Map
                ---
                """,
                     style={
                         'font-family': 'plain light',
                         'color': 'grey',
                         'font-weight': 'light'
                     }),
        html.Br(),
        html.Br(),
        dbc.Row([
                dbc.Col([
                    html.Label('Market Developer',
                               style={
                                   'font-family': 'plain',
                                   'font-weight': 'light'
                               }),
                    dcc.Dropdown(id='MD Dropdown',
                                 options=[{
                                     'label': 'All MDs',
                                     'value': 'All MDs'
                                 }],
                                 value=['All MDs'],
                                 multi=True,
                                 style={
                                     'font-family': 'plain',
                                     'font-weight': 'light',
                                     'width': '300px'
                                 })
                ],
                    width=4),
                dbc.Col([
                    html.Label('Ride Type',
                               style={
                                   'font-family': 'plain',
                                   'font-weight': 'light'
                               }),
                    dcc.Dropdown(id='Ride Type Dropdown',
                                 options=[{
                                     'label': 'All',
                                     'value': 'All'
                                 }],
                                 value=['All'],
                                 multi=True,
                                 style={
                                     'font-family': 'plain',
                                     'font-weight': 'light',
                                     'width': '300px'
                                 })
                ],
                    width=4)
                ]),
        html.Br(),
        dbc.Row([
                dbc.Col(
                    html.H2('Total Butts on Bikes',
                            style={
                                'font-family': 'plain',
                                'font-weight': 'light',
                                'color': 'grey',
                                'text-align': 'center',
                                'font-size': 24,
                                'textAlign': 'center'
                            }),
                    align="center", width=3),
                dbc.Col(
                    html.H2('Total Activations:',
                            style={
                                'font-family': 'plain',
                                'font-weight': 'light',
                                'color': 'grey',
                                'font-size': 24,
                                'textAlign': 'center'
                            }),
                    align="center", width=3),
                dbc.Col(
                    html.H2('Total Staff Educated:',
                            style={
                                'font-family': 'plain',
                                'font-weight': 'light',
                                'color': 'grey',
                                'font-size': 24,
                                'textAlign': 'center'
                            }),
                    align="center", width=3),
                ], justify='center', style={'padding-top': 100}),
        dbc.Row([
                dbc.Col(
                    html.H1(id='label_filtered_bob',
                               style={
                                   'font-family': 'plain light',
                                   'font-weight': 'light',
                                   'font-size': 36,
                                   'padding': 0,
                                   'textAlign': 'center'
                               }), align="center", width=3),
                dbc.Col(
                    html.H1(id='label_filtered_activations',
                               style={
                                   'font-family': 'plain light',
                                   'font-weight': 'light',
                                   'font-size': 36,
                                   'padding': 0,
                                   'textAlign': 'center'
                               }), align="center", width=3),
                dbc.Col(
                    html.H1(id='label_filtered_staff',
                               style={
                                   'font-family': 'plain light',
                                   'font-weight': 'light',
                                   'font-size': 36,
                                   'padding': 0,
                                   'textAlign': 'center'
                               }), align="center", width=3),
                ], style={'t-padding': 0}, justify='center'),
        dbc.Row([
                dbc.Col([
                    dcc.Graph(id='second_map', style={'height': '800px'})
                ])
                ]),
        dcc.Markdown("""
                # Bonus Tracker
                ---
                """,
                     style={
                         'font-family': 'plain light',
                         'color': 'grey',
                         'font-weight': 'light'
                     }),
        html.Br(),
        html.Br(),
        dbc.Row(
            dbc.Col([
                    html.Label("Quarter:",
                               style={
                                   'font-family': 'plain',
                                   'font-weight': 'light'
                               }),
                    dcc.Dropdown(id='quarter_dropdown',
                                 options=[
                                     {'label': '2020 Q3', 'value': '2020 Q3'}],
                                 value='2020 Q3',
                                 multi=False,
                                 style={
                                     'font-family': 'plain light',
                                     'font-weight': 'light',
                                     'padding': 2
                                 })
                    ], width=4)
        ),
        html.Br(),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='bonus_table',
                    columns=bonus_col,
                    data=[],
                    virtualization=False,
                    page_action='none',
                    # filter_action="native",
                    sort_action="native",
                    sort_mode="single",
                    row_selectable='multi',
                    row_deletable=False,
                    style_cell={
                        # 'minWidth': 10,
                        # 'maxWidth': 65,
                        'fontSize': FONTSIZE,
                        'padding': CELL_PADDING,
                    },
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold',
                        'font-family': 'plain',
                        # 'maxWidth': 65,
                        # 'minWidth': 10,
                        'textAlign': 'center',
                        'padding': CELL_PADDING,
                    },
                    style_cell_conditional=bonus_cell_cond,
                    style_data={
                        'whiteSpace': 'normal',
                        # 'height': 'auto',
                        'font-family': 'plain light',
                        'font-weight': 'light',
                        'color': 'grey',
                        'padding': DATA_PADDING,
                        # 'minWidth': 10,
                    },
                    style_data_conditional=bonus_data_cond,
                    style_table={
                        # 'overflowX': 'scroll',
                        # 'height': '1000px',
                        # 'width': '90%',
                        'page_size': 10,
                        'minWidth': 10,
                        'padding': TABLE_PADDING
                    },
                    # fixed_rows={'headers': True},
                    style_as_list_view=True,
                    export_columns='visible',
                    export_format='csv'
                )
            )
        ),
        dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='total_bob_bar',
                    )
                ], width=6),
                dbc.Col([
                    dcc.Graph(
                        id='activations_bar',
                    )
                ], width=6)
                ]),
        dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='clinics_bar',
                    )
                ], width=6),
                dbc.Col([
                    dcc.Graph(
                        id='trail_bar',
                    )
                ], width=6)
                ]),
        dcc.Markdown("""
                # Export all data in this date range: 
                ---
                """,
                     style={
                         'font-family': 'plain light',
                         'color': 'grey',
                         'font-weight': 'light'
                     }),
        html.Br(),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='main_table',
                    columns=[],
                    data=[],
                    virtualization=True,
                    page_action='none',
                    filter_action="native",
                    sort_action="native",
                    sort_mode="single",
                    row_selectable=False,
                    row_deletable=False,
                    style_cell={
                        # 'minWidth': 10,
                        # 'maxWidth': 65,
                        'fontSize': 10,
                        'padding': CELL_PADDING,
                    },
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold',
                        'font-family': 'plain',
                        # 'maxWidth': 65,
                        # 'minWidth': 10,
                        'textAlign': 'center',
                        'padding': CELL_PADDING,
                    },
                    style_cell_conditional=bonus_cell_cond,
                    style_data={
                        'whiteSpace': 'normal',
                        # 'height': 'auto',
                        'font-family': 'plain light',
                        'font-weight': 'light',
                        'color': 'grey',
                        'padding': DATA_PADDING,
                        # 'minWidth': 10,
                    },
                    style_data_conditional=bonus_data_cond,
                    style_table={
                        'overflowX': 'scroll',
                        'height': '500px',
                        # 'width': '90%',
                        'page_size': 10,
                        'minWidth': 10,
                        'padding': TABLE_PADDING
                    },
                    fixed_rows={'headers': True},
                    style_as_list_view=True,
                    export_columns='visible',
                    export_format='csv'
                )
            )
        ),
        dbc.Row(
            dbc.Col([
                html.Img(id="sLogo",
                         src="./assets/Specialized_black_S.jpg",
                         alt="Specialized Wordmark logo",
                         style={
                            #  'width': '30%',
                             'height': '20%'
                         }),
            ], width={"size": 2, "offset": 5}),
        ),

        html.Div(id='intermediate_value_date', style={'display': 'none'}),
        html.Div(id='intermediate_value_quarter',
                 style={'display': 'none'}),
        html.Div(id='intermediate_value_quarter_bar',
                 style={'display': 'none'}),
    ]
    ), style={"padding": "100px"})


@ app.callback(
    Output('label_total_bob', 'children'),
    [Input('intermediate_value_date', 'children')]
)
def label_total_bob(jsonified_cleaned_data):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    total_bob = df[['demo_bob', 'festival_bob', 'vip_bob',
                    'other_event_bob']].sum().sum()
    text = f'''{total_bob}'''
    return text


@ app.callback(
    Output('label_total_activations', 'children'),
    [Input('intermediate_value_date', 'children')]
)
def label_total_activations(jsonified_cleaned_data):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    total_activations = len(df)
    text = f'''{total_activations}'''
    return text


@ app.callback(
    Output('label_total_staff', 'children'),
    [Input('intermediate_value_date', 'children')]
)
def label_total_staff(jsonified_cleaned_data):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    total_staff = df['staff_count'].sum()
    text = f'''{total_staff}'''
    return text


@ app.callback(
    Output('main_map', 'figure'),
    [Input('intermediate_value_date', 'children')]
)
def build_main_map(jsonified_cleaned_data):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    scale = .07
    main = [('demo_bob', "Demo"),
            ('staff_count', "Clinic"),
            ('festival_bob', 'Festival'),
            ('vip_bob', 'VIP Event'),
            ('trail_building_total_attendance', "Trail Day"),
            ('other_event_bob', 'Other Test Rides')]
    fig = go.Figure()
    for i in main:
        key = i[0]
        name = i[1]
        fig.add_trace(go.Scattergeo(
            lon=df.loc[df[key] > 0, 'longitude'],
            lat=df.loc[df[key] > 0, 'latitude'],
            text=df.loc[df[key] > 0, 'market_developer'],
            customdata=df[key].loc[df[key] > 0],
            marker=dict(
                size=df[key].loc[df[key] > 0]/scale,
                # color = colors[i],
                line_color='rgb(40,40,40)',
                line_width=0.9,
                sizemode='area'
            ),
            hovertemplate="MD: <b>%{text}</b><br><br>" +
            "Audience: %{customdata}<br>" +
            '<extra></extra>',
            name=name
        )
        )
    fig.add_trace(go.Scattergeo(
        lon=df.loc[~df['shop_assist_retail_partner'].isnull(),
                   'longitude'],
        lat=df.loc[~df['shop_assist_retail_partner'].isnull(), 'latitude'],
        text=df.loc[~df['shop_assist_retail_partner'].isnull(),
                    'market_developer'],
        customdata=df['shop_assist_retail_partner'].loc[~df['shop_assist_retail_partner'].isnull()],
        marker=dict(
            symbol='star-diamond',
            size=10,
            # color = colors[i],
            line_color='rgb(40,40,40)',
            line_width=0.9,
            sizemode='area'
        ),
        hovertemplate="MD: <b>%{text}</b><br><br>" +
        "Shop Name: %{customdata}<br>" +
        '<extra></extra>',
        name="Shop Assist"
    )
    )
    fig.update_layout(
        plot_bgcolor='Black',
        showlegend=True,
        geo=dict(
            bgcolor='black',
            resolution=110,
            scope='usa',
            landcolor='white',
            showland=True,
            showocean=False,
            showcoastlines=True,
        )
    )
    return fig


@ app.callback(
    Output('MD Dropdown', 'options'),
    [Input('intermediate_value_date', 'children')]
)
def build_MD_dropdown(jsonified_cleaned_data):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    LIST = [{'label': 'All MDs', 'value': 'All MDs'}]
    TEMP = list(df['market_developer'].unique())
    for i in TEMP:
        LIST.append({"label": i, "value": i})
    return LIST


@ app.callback(
    Output('Ride Type Dropdown', 'options'),
    [Input('intermediate_value_date', 'children')]
)
def build_ride_type_dropdown(jsonified_cleaned_data):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    LIST = [{'label': 'All', 'value': 'All'}]
    TEMP = list(df['discipline'].unique())
    for i in TEMP:
        LIST.append({"label": i, "value": i})
    return LIST


@ app.callback(
    Output('label_filtered_bob', 'children'),
    [Input('intermediate_value_date', 'children'),
     Input('MD Dropdown', 'value'),
     Input('Ride Type Dropdown', 'value')]
)
def label_filtered_bob(jsonified_cleaned_data, MD, ride_type):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    if MD == ['All MDs']:
        MD = list(df['market_developer'].unique())
    if ride_type == ['All']:
        ride_type = list(df['discipline'].unique())
    df = df.loc[(df['market_developer'].isin(MD)) &
                (df['discipline'].isin(ride_type))]

    filtered_bob = df[['demo_bob', 'festival_bob', 'vip_bob',
                       'other_event_bob']].sum().sum()
    text = f'''{filtered_bob}'''
    return text


@ app.callback(
    Output('label_filtered_activations', 'children'),
    [Input('intermediate_value_date', 'children'),
     Input('MD Dropdown', 'value'),
     Input('Ride Type Dropdown', 'value')]
)
def label_filtered_activations(jsonified_cleaned_data, MD, ride_type):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    if MD == ['All MDs']:
        MD = list(df['market_developer'].unique())
    if ride_type == ['All']:
        ride_type = list(df['discipline'].unique())
    df = df.loc[(df['market_developer'].isin(MD)) &
                (df['discipline'].isin(ride_type))]
    filtered_activations = len(df)
    text = f'''{filtered_activations}'''
    return text


@ app.callback(
    Output('label_filtered_staff', 'children'),
    [Input('intermediate_value_date', 'children'),
     Input('MD Dropdown', 'value'),
     Input('Ride Type Dropdown', 'value')]
)
def label_filtered_staff(jsonified_cleaned_data, MD, ride_type):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    if MD == ['All MDs']:
        MD = list(df['market_developer'].unique())
    if ride_type == ['All']:
        ride_type = list(df['discipline'].unique())
    df = df.loc[(df['market_developer'].isin(MD)) &
                (df['discipline'].isin(ride_type))]
    filtered_staff = df['staff_count'].sum()
    text = f'''{filtered_staff}'''
    return text


@ app.callback(
    Output('second_map', 'figure'),
    [Input('intermediate_value_date', 'children'),
     Input('MD Dropdown', 'value'),
     Input('Ride Type Dropdown', 'value')]
)
def build_second_map(jsonified_cleaned_data, MD, ride_type):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    scale = .07
    if MD == ['All MDs']:
        MD = list(df['market_developer'].unique())
    if ride_type == ['All']:
        ride_type = list(df['discipline'].unique())
    df = df.loc[(df['market_developer'].isin(MD)) &
                (df['discipline'].isin(ride_type))]

    df['agg'] = df[['demo_bob', 'staff_count', 'festival_total_attendance',
                    'festival_bob', 'vip_total_attendance', 'vip_bob',
                    'other_event_bob']].sum(axis=1)

    fig = go.Figure()
    scale = .1
    for i in ride_type:
        fig.add_trace(go.Scattergeo(
            lon=df.loc[df['discipline'] == i, 'longitude'],
            lat=df.loc[df['discipline'] == i, 'latitude'],
            text=df.loc[df['discipline'] == i, 'market_developer'],
            customdata=df['agg'].loc[df['discipline'] == i],
            marker=dict(
                size=df['agg'].loc[df['discipline'] == i]/scale,
                # color = colors[i],
                line_color='rgb(40,40,40)',
                line_width=0.9,
                sizemode='area'
            ),
            hovertemplate="MD: <b>%{text}</b><br><br>" +
            "Audience: %{customdata}<br>" +
            '<extra></extra>',
            name=i
        )
        )
    fig.add_trace(go.Scattergeo(
        lon=df.loc[~df['shop_assist_retail_partner'].isnull(),
                   'longitude'],
        lat=df.loc[~df['shop_assist_retail_partner'].isnull(), 'latitude'],
        text=df.loc[~df['shop_assist_retail_partner'].isnull(),
                    'market_developer'],
        customdata=df['shop_assist_retail_partner'].loc[~df['shop_assist_retail_partner'].isnull()],
        marker=dict(
            symbol='star-diamond',
            size=10,
            # color = colors[i],
            line_color='rgb(40,40,40)',
            line_width=0.9,
            sizemode='area'
        ),
        hovertemplate="MD: <b>%{text}</b><br><br>" +
        "Shop Name: %{customdata}<br>" +
        '<extra></extra>',
        name="Shop Assist"
    )
    )
    fig.update_layout(
        plot_bgcolor='Black',
        showlegend=True,
        geo=dict(
            bgcolor='black',
            resolution=110,
            scope='usa',
            landcolor='white',
            showland=True,
            showocean=False,
            showcoastlines=True,
        )
    )
    return fig


@ app.callback(
    Output('quarter_dropdown', 'options'),
    [Input('intermediate_value_date', 'children')]
)
def build_quater_dropdown(jsonified_cleaned_data):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    LIST = [{'label': '2020 Q3', 'value': '2020 Q3'}]
    TEMP = list(df['year_quarter'].unique())
    for i in TEMP:
        LIST.append({"label": i, "value": i})
    return LIST


@ app.callback(
    Output('bonus_table', 'data'),
    [Input('intermediate_value_quarter', 'children')]
)
def build_bonus_table(jsonified_cleaned_data):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    clinics = df.loc[df['activation_type'] == 'Clinic'].groupby(
        ['market_developer']).agg({'event': 'count'})
    activations = df.loc[(df['activation_type'] != 'Clinic') & (
        df['activation_type'] != 'Trail Day')].groupby(['market_developer']).agg({'event': 'count'})
    trail_day = df.loc[df['activation_type'] == 'Trail building day'].groupby(
        ['market_developer']).agg({'event': 'count'})
    df = pd.DataFrame(data={'market_developer': list(df.market_developer),
                            'total_bob': list(df[['demo_bob', 'festival_bob', 'vip_bob', 'other_event_bob']].sum(axis=1))
                            }
                      ).set_index('market_developer')
    df = df.groupby('market_developer').sum()
    df = df.join(clinics, rsuffix='clinics')
    df = df.join(activations, rsuffix='activation')
    df = df.join(trail_day, rsuffix='trail_day')
    df.columns = ['total_bob', 'clinics', 'activation', 'trail_day']
    df.reset_index(inplace=True)
    df = df.to_dict('records')
    return df


@app.callback([
    Output('total_bob_bar', 'figure'),
    Output('activations_bar', 'figure'),
    Output('clinics_bar', 'figure'),
    Output('trail_bar', 'figure')],
    [Input('intermediate_value_quarter', 'children'),
     Input('bonus_table', "derived_virtual_data"),
     Input('bonus_table', 'derived_virtual_selected_rows'),
     Input('bonus_table', 'selected_rows')]
)
def build_bar(jsonified_cleaned_data, all_rows_data, slctd_row_indices, slctd_rows):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    md_name = "All"
    if slctd_row_indices:
        md_name = (all_rows_data[slctd_row_indices[0]]['market_developer'])
        df = df.loc[df['market_developer'] == md_name]
    clinics = df.loc[df['activation_type'] == 'Clinic'].groupby(
        ['Week']).agg({'event': 'count'})
    activations = df.loc[(df['activation_type'] != 'Clinic') & (
        df['activation_type'] != 'Trail Day')].groupby(['Week']).agg({'event': 'count'})
    trail_day = df.loc[df['activation_type'] == 'Trail building day'].groupby(
        ['Week']).agg({'event': 'count'})
    df = pd.DataFrame(data={'Week': list(df.Week),
                            'total_bob': list(df[['demo_bob', 'festival_bob', 'vip_bob', 'other_event_bob']].sum(axis=1))
                            }
                      ).set_index('Week')
    df = df.groupby('Week').sum()
    df = df.join(clinics, rsuffix='clinics')
    df = df.join(activations, rsuffix='activation')
    df = df.join(trail_day, rsuffix='trail_day')
    df.columns = ['total_bob', 'clinics', 'activation', 'trail_day']
    df = df.fillna(0)

    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(
            x=df.index,
            y=df.total_bob,
            marker_color='rgba(168, 168, 168, 0.7)',
            name='Total B.O.B.',
            text=df.total_bob,
            textposition='auto',
            hovertemplate='<b>Week</b>:   %{x}' +
                          '<br>Count:  %{y}')
    )
    fig1.update_layout(title=f'Total Butts on Bikes - {md_name}')
    fig1.update_xaxes(title='Week', showgrid=False, zeroline=False)
    fig1.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=df.index,
            y=df.activation,
            name='Total Activations',
            marker_color='#19d3f3',
            text=df.activation,
            textposition='auto',
            hovertemplate='<b>Week</b>:   %{x}' +
                          '<br>Count:  %{y}')
    )
    fig2.update_layout(title=f'Total Activations - {md_name}')
    fig2.update_xaxes(title='Week', showgrid=False, zeroline=False)
    fig2.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=df.index,
            y=df.clinics,
            name='Total Activations',
            marker_color='#00cc96',
            text=df.clinics,
            textposition='auto',
            hovertemplate='<b>Week</b>:   %{x}' +
                          '<br>Count:  %{y}')
    )
    fig3.update_layout(title=f'Total Clinics - {md_name}')
    fig3.update_xaxes(title='Week', showgrid=False, zeroline=False)
    fig3.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    fig4 = go.Figure()
    fig4.add_trace(
        go.Bar(
            x=df.index,
            y=df.trail_day,
            name='Total Trail Days',
            marker_color='#ab63fa',
            text=df.trail_day,
            textposition='auto',
            hovertemplate='<b>Week</b>:   %{x}' +
                          '<br>Count:  %{y}')
    )
    fig4.update_layout(title=f'Total Trail Building Days - {md_name}')
    fig4.update_xaxes(title='Week', showgrid=False, zeroline=False)
    fig4.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig1, fig2, fig3, fig4


@ app.callback([
    Output('main_table', 'data'),
    Output('main_table', 'columns'), ],
    [Input('intermediate_value_date', 'children')]
)
def build_main_table(jsonified_cleaned_data):
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    columns = [{"name": i, "id": i} for i in df.columns]
    return df.to_dict('records'), columns


@ app.callback(
    Output('intermediate_value_date', 'children'),
    [Input('dt-picker-range', 'start_date'),
     Input('dt-picker-range', 'end_date')])
def clean_data(start_date, end_date):
    # some expensive data pull step
    gsheet = get_google_sheet()
    df = gsheet2df(gsheet)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = pd.to_datetime(df.date)
    df['Week'] = df['date'].dt.isocalendar().week
    df['quarter'] = df['date'].dt.quarter.astype(str)
    df['year'] = df['date'].dt.year.astype(str)
    df['year_quarter'] = df['year'] + " Q" + df['quarter']
    temp = df.loc[(df['date'] > start_date)
                  & (df['date'] < end_date)].copy()
    integers = ['demo_bob', 'festival_bob', 'vip_bob',
                'other_event_bob', 'staff_count',
                'trail_building_total_attendance']
    temp[integers] = temp[integers].replace(
        '', 0).replace('None', 0).astype(int)
    temp = temp.replace('', np.nan).replace('None', np.nan)
    print(temp)
    return temp.to_json(date_format='iso', orient='split')


@ app.callback(
    [Output('intermediate_value_quarter', 'children'),
     Output('intermediate_value_quarter_bar', 'children')],
    [Input('quarter_dropdown', 'value')]
)
def clean_quarter_data(quarter):
    # some expensive data pull step
    gsheet = get_google_sheet()
    df = gsheet2df(gsheet)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = pd.to_datetime(df.date)
    df['Week'] = df['date'].dt.isocalendar().week
    df['quarter'] = df['date'].dt.quarter.astype(str)
    df['year'] = df['date'].dt.year.astype(str)
    df['year_quarter'] = df['year'] + " Q" + df['quarter']
    integers = ['demo_bob', 'festival_bob', 'vip_bob',
                'other_event_bob', 'staff_count',
                'trail_building_total_attendance']
    df[integers] = df[integers].replace(
        '', 0).replace('None', 0).astype(int)
    df = df.replace('', np.nan).replace('None', np.nan)
    df = df.loc[df['year_quarter'] == quarter]
    df = df.to_json(date_format='iso', orient='split')
    return df, df


if __name__ == '__main__':
    app.run_server(debug=True, port=4050)
