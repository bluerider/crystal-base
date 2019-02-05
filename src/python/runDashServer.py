import os, datetime, base64, sys
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table_experiments as dash_table
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
from classifyImagesMarcoPartitionOneOff import classifyImagesMarcoPartitionOneOff

## start the app
app = dash.Dash()
app.scripts.config.serve_locally = True

host = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
dbname = sys.argv[4]
db = create_engine('postgresql://%s:%s@%s:5432/%s'%(user, password, host, dbname))

app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Upload images'
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Button('Demo', id='demo',
               style={
                   'width' : '100%',
                   'textAlign' : 'center'
               }),
    html.Div([
        html.Div(id='live-update-text'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000,
            n_intervals=0)
    ]),
    html.Div(id='output-image-upload'),
])

def resizeImgs(imgs):
    resized_imgs = []
    ## generate the base64 string padding string
    padding = "data:image/jpeg;base64,"
    for img in imgs:
        ## read the image as a byte array
        image = Image.open(io.BytesIO(img))
        resized_img = image.resize(400,300)
        ## open a new jpeg buffer
        jpeg_buffer = io.ByteIO()
        ## save the image as a jpeg file
        resized_img.save(jpeg_buffer, format = "JPEG")
        ## we need to convert the jpeg file to base64
        ## and append to array
        resized_imgs += padding + str(base64.b64encode(jpeg_buffer))[2:]
    ## return the resized images
    return(resized_imgs)

def parse_contents(contents, values, date, ):
    name, crystal_bool = values
    return html.Div([
        html.H5(name),
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents),
        html.Hr(),
        html.Div('Prediction : '+str(crystal_bool)),
        #html.Pre(contents[0:200] + '...', style={
        #    'whiteSpace': 'pre-wrap',
        #    'wordBreak': 'break-all'
        #})
    ])

@app.callback(Output('output-image-upload', 'children'),
              [Input('upload-image', 'contents')],
              [State('upload-image', 'filename'),
               State('upload-image', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        ## get the raw image byte date
        imgs = [base64.b64decode(img[23:]) for img in list_of_contents]
        ## classify the images
        values = classifyImagesMarcoPartitionOneOff(zip(list_of_names, imgs))
        ## we got to resize the pictures to form a grid that will fit
        #resized_imgs = resizeImgs(imgs)
        resized_imgs = list_of_contents
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(resized_imgs, values, list_of_dates)]
        return children

## update text
@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    with db.connect() as con:
        sql_query = """
            SELECT count(*) FROM marcos where crystal is true;
            """
        positive_count = str(con.execute(sql_query).fetchone()[0])
        sql_query = """
            SELECT count(*) FROM marcos where crystal is false;
            """
        negative_count = str(con.execute(sql_query).fetchone()[0])
    return html.Div([
        html.Span('Positive: '+positive_count+"     Negative: "+negative_count),
    ])
    

if __name__ == '__main__':
    ## run the app as a server
    app.run_server(debug=True, port=5000, host = '0.0.0.0')