import os, datetime, base64, sys
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table_experiments as dash_table
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
from classifyImagesMarcoPartitionOneOff import classifyImagesMarcoPartitionOneOff

## start the ap
app = dash.Dash(__name__, 
                static_folder = 'static',
                external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Crystal-Base"
app.scripts.config.serve_locally = True

## setup the postgres connector
host = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
dbname = sys.argv[4]
db = create_engine('postgresql://%s:%s@%s:5432/%s'%(user, password, host, dbname))

## setup the navigation bar
navbar = dbc.NavbarSimple(
    children = [html.Div([dbc.NavItem(id = 'sql_count'),
                          dcc.Interval(id = 'interval-component',
                                       interval = 1*1000,
                                       n_intervals = 0)],
                         style = {'padding-left' : '10px',
                                  'padding-right' : '10px'}),
                html.A([html.Img(src='/static/GitHub-Mark-32px.png')],
                       href = 'https://github.com/bluerider/crystal-base',
                       target = "_blank")],
    brand = "Crystal-Base",
    brand_href = '#',
    sticky = "top",
    color = "#6699ff")

## setup the body of the document
body = dbc.Container(
    [html.Div([dcc.Upload(id = 'upload-image',
                          children=html.Div(['Upload images']),
                          style = {'lineHeight': '60px',
                                   'borderStyle': 'dashed',
                                   'borderRadius': '5px',
                                   'textAlign': 'center'},
                                  ## allow uploading multiple files
                          multiple = True)]),
     html.Div(id = 'output-image-upload')
    ])

## set the app layout
app.layout = html.Div([navbar, body])

## parse the contents of passed images and
## return a html divider
def parse_contents(contents, values, date, ):
    """
    Return a HTML divider for prediction results
    and the uploaded image.
    """
    name, crystal_bool = values
    return html.Div([
        html.Hr(),
        html.H5(name+"; Prediction: "+str(crystal_bool)),
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents),
        html.Hr()
    ])

## call back for upload images
@app.callback(Output('output-image-upload', 'children'),
              [Input('upload-image', 'contents')],
              [State('upload-image', 'filename'),
               State('upload-image', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    """
    Classify uploaded images.
    Returns classification of images as well as the image itself
    for display on web app.
    """
    if list_of_contents is not None:
        ## get the raw image byte date
        imgs = [base64.b64decode(img[23:]) for img in list_of_contents]
        ## classify the images
        values = classifyImagesMarcoPartitionOneOff(zip(list_of_names, imgs))
        ## we got to resize the pictures to form a grid that will fit
        resized_imgs = list_of_contents
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(resized_imgs, values, list_of_dates)]
        return children
    
## update text
@app.callback(Output('sql_count', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    """
    Connect to postgres and get the current number of classified images.
    Return the count for negative and positive results for display
    in the web app.
    """
    with db.connect() as con:
        sql_query = """
            SELECT count(*) FROM marcos where crystal is true;
            """
        positive_count = str(con.execute(sql_query).fetchone()[0])
        sql_query = """
            SELECT count(*) FROM marcos where crystal is false;
            """
        negative_count = str(con.execute(sql_query).fetchone()[0])
    return html.Div([dbc.Button("Crystals: "+positive_count,
                                 color = "success"),
                     dbc.Button("Junk: "+negative_count,
                                color = "secondary")])

if __name__ == '__main__':
    """
    Run the app.
    """
    ## run the app as a server
    ## use 5001 to avoid screwing
    ## with the currently running server
    app.run_server(port=5000, host = '0.0.0.0')