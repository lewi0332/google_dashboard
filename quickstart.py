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
import dash_auth
from dash.dependencies import Input, Output
from flask import Flask
import fohr_theme_light
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1L2Y_7Blru9bHCOA4QxGW9QrL0B1pzKvlge4YRcsKrm4'
RANGE_NAME = 'Form Responses 1!A1:K'


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


gsheet = get_google_sheet()
df = gsheet2df(gsheet)
df['Rider count'] = df['Rider count'].astype(int)

types_ = ['Clinic', 'Demo']
scale = 1

fig = go.Figure()

for i in range(len(types_)):
    type_ = types_[i]
    df_sub = df.loc[df['Type of Activation'] == type_]
    fig.add_trace(go.Scattergeo(
        locationmode='USA-states',
        lon=df_sub['Longitude'],
        lat=df_sub['Latitude'],
        text=df_sub['Demo Name'],
        marker=dict(
            size=df_sub['Rider count']/scale,
            # color=colors[i],
            line_color='rgb(40,40,40)',
            line_width=0.9,
            sizemode='area'
        ),
        name=f'{type_}'
    )
    )

fig.update_layout(
    title_text='Market Development Activity',
    plot_bgcolor='white',
    showlegend=True,
    geo=dict(
        resolution=110,
        scope='usa',
        landcolor='white',
        showland=True,
        showocean=True,
        showcoastlines=True,
    )
)


server = Flask(__name__)
VALID_USERNAME_PASSWORD_PAIRS = {'demo': 'testthebest'}

app = Dash(name=__name__,
           server=server,
           external_stylesheets=[dbc.themes.GRID])

app.config.suppress_callback_exceptions = False
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

app.layout = html.Div(
    html.Div(
        [
            dcc.Markdown("""
                        ---
                        # Stoke-o-Meter Dashboard
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
            dcc.DatePickerRange(id='dt-picker-range',
                                start_date=datetime.now() - timedelta(days=90),
                                end_date=datetime.now()),
            html.Br(),
            html.Br(),
            html.Br(),
            dcc.Markdown("""
                        ---
                        # Testing
                        ---
                        """,
                         style={
                             'font-family': 'plain light',
                             'color': 'grey',
                             'font-weight': 'light'
                         }),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Label('Region',
                               style={
                                   'font-family': 'plain',
                                   'font-weight': 'light'
                               }),
                    dcc.Dropdown(id='Region Dropdown',
                                 options=[{
                                     'label': 'US',
                                     'value': 'True'
                                 }, {
                                     'label': 'R.O.W.',
                                     'value': 'False'
                                 }],
                                 value=['True'],
                                 multi=True,
                                 style={
                                     'font-family': 'plain',
                                     'font-weight': 'light',
                                     'width': '300px'
                                 })
                ],
                    width=3),
                dbc.Col([
                    html.Label('Type',
                               style={
                                   'font-family': 'plain',
                                   'font-weight': 'light'
                               }),
                    dcc.Dropdown(id='IG Type Dropdown',
                                 options=[{
                                     'label': 'Clinic',
                                     'value': 'Clinic'
                                 }, {
                                     'label': 'Demo',
                                     'value': 'Demo'
                                 }],
                                 value=['Clinic', 'Demo'],
                                 multi=False,
                                 style={
                                     'font-family': 'plain',
                                     'font-weight': 'light',
                                     'width': '300px'
                                 })
                ],
                    width=3)
            ]),
            html.Br(),
            html.Br(),
            html.Br(),
            dcc.Markdown("""
                ---
                # Content by User
                ---
                """,
                         style={
                             'font-family': 'plain light',
                             'color': 'grey',
                             'font-weight': 'light'
                         })
        ]
    ))

if __name__ == '__main__':
    app.run_server(debug=True, port=4050)
