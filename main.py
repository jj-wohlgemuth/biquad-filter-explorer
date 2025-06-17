import numpy as np
import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import analyze
from dash.dependencies import Input, Output

number_labels = {'Sampling Frequency in Hz': 'fs_hz',
                 'Significant Frequency in Hz': 'frequency_hz',
                 'Filter Gain in dB': 'gain_db',
                 'Q': 'q'}

types = [{'label': 'Band', 'value': 'PEAKING'},
         {'label': 'Lowpass', 'value': 'LOWPASS'},
         {'label': 'Highpass', 'value': 'HIGHPASS'},
         {'label': 'Bandpass const. skirt', 'value': 'BANDPASS_SKIRT'},
         {'label': 'Bandpass const. peak', 'value': 'BANDPASS_PEAK'},
         {'label': 'Notch', 'value': 'NOTCH'},
         {'label': 'Allpass', 'value': 'ALLPASS'},
         {'label': 'Lowshelf', 'value': 'LOWSHELF'},
         {'label': 'Highshelf', 'value': 'HIGHSHELF'}]

default = {'Type': 'PEAKING'}

dropdown_options = {'Type': types}

dropdown_labels = {'Type': 'f_type'}

min_max_default = {'f_type': [],
                   'fs_hz': [1, 10e12, 48e3],
                   'frequency_hz': [1e-12, 5e12, 440],
                   'gain_db': [-120, 120, 6],
                   'q': [0, 32, 1/np.sqrt(2)]}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

inputs = [[html.Label(label),
           dcc.Input(id=number_labels[label],
                     type='number',
                     min=min_max_default[number_labels[label]][0],
                     max=min_max_default[number_labels[label]][1],
                     value=min_max_default[number_labels[label]][2],
                     style={'width': '90%'})]
          for label in number_labels]
width = str(100/len(inputs)) + '%'
input_children = [html.Div(children=i,
                           style={'width': width,
                                  'display': 'inline-block'})
                  for i in inputs]

dropdowns = [[html.Label(dl),
             dcc.Dropdown(id=dropdown_labels[dl],
                          options=dropdown_options[dl],
                          value=default[dl],
                          style={'width': '90%'})]
             for dl in dropdown_labels]
dropdown_children = [html.Div(children=i,
                              style={'width': width,
                                     'display':
                                     'inline-block'})
                     for i in dropdowns]

top_layout = [html.Div(children=input_children +
                       [html.Div(children=[html.Br()])] +
                       dropdown_children +
                       [html.Div(children=[html.Br()])],
                       style={'width': '100%',
                              'height': '10%'})]
pole_zero_fig = go.Figure()
pole_zero_fig.add_shape(type="circle",
                        xref="x",
                        yref="y",
                        x0=-1,
                        y0=-1,
                        x1=1,
                        y1=1,
                        line_color="#7F7F7F")

btm_cldrn = [dcc.Graph(id='mag',
                       style={'height': '35vh',
                              'width': '100%'})] +\
            [dcc.Graph(id='phase',
                       style={'height': '35vh',
                              'width': '57vh',
                              'display': 'inline-block'})] +\
            [dcc.Graph(id='gd',
                       style={'height': '35vh',
                              'width': '57vh',
                              'display': 'inline-block'})] +\
            [dcc.Graph(id='pole_zero',
                       style={'height': '40vh',
                              'width': '40vh',
                              'display': 'inline-block'})] +\
            [dcc.Textarea(id='textarea',
                          style={'width': '40vh',
                                 'height': '30vh',
                                 'margin-left': '5vh',
                                 'margin-bottom': '5vh',
                                 'whiteSpace': 'pre-line',
                                 'display': 'inline-block'})]

bottom_layout = [html.Div(children=btm_cldrn, style={'width': '100%'})]
app.layout = html.Div(children=top_layout + bottom_layout,
                      style={'width': '100%'})


@app.callback(
    [Output('mag', 'figure'),
     Output('phase', 'figure'),
     Output('gd', 'figure'),
     Output('pole_zero', 'figure'),
     Output('textarea', 'value')],
    [Input(label, 'value') for label in min_max_default])
def update_mag(eq_type, fs_hz, frequency_hz, gain_db, q):
    z, p, b, a, frequency_hz, amplitude_dB, angle_deg, gd_samples =\
        analyze.get_plot_data(eq_type, fs_hz, frequency_hz, gain_db, q)
    out_string = 'b = ' + str(b) +\
                 '\na = ' + str(a)
    pole_zero_fig.data = []
    pole_zero_fig.add_trace(go.Scatter(x=np.real(z),
                                       y=np.imag(z),
                                       mode='markers',
                                       name='zeros'))
    pole_zero_fig.add_trace(go.Scatter(x=np.real(p),
                                       y=np.imag(p),
                                       mode='markers',
                                       name='poles'))
    pole_zero_fig['layout']['xaxis'].update(title='Real part',
                                            autorange=False,
                                            range=[-1.5, 1.5],
                                            gridcolor='#EEEEEE',
                                            linecolor='white',
                                            zerolinecolor='#444444')
    pole_zero_fig['layout']['yaxis'].update(title='Imaginary part',
                                            autorange=False,
                                            range=[-1.5, 1.5],
                                            gridcolor='#EEEEEE',
                                            linecolor='white',
                                            zerolinecolor='#444444')
    pole_zero_fig.update_layout(plot_bgcolor='white')
    traces = [
                dict(x=frequency_hz[:-1],
                     y=amplitude_dB[:-1],
                     name='magnitude',
                     text=eq_type,
                     mode='line',
                     marker={'size': 10,
                             'color': 'black'},
                     opacity=0.5),
                dict(x=frequency_hz[:-1],
                     y=angle_deg[:-1],
                     name='angle',
                     text=eq_type,
                     mode='line',
                     marker={'size': 10,
                             'color': 'black'},
                     opacity=0.5),
                dict(x=frequency_hz[:-1],
                     y=gd_samples[:-1],
                     name='angle',
                     text=eq_type,
                     mode='line',
                     marker={'size': 10,
                             'color': 'black'},
                     opacity=0.5),
             ]

    return [
        {
            'data': [traces[0]],
            'layout': dict(xaxis={'type': 'log',
                                  'title': 'Frequency in Hz'},
                           yaxis={'title': 'Magnitude in dB'},
                           margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                           legend={'x': 0, 'y': 1},
                           hovermode='closest',
                           transition={'duration': 500},
                           )
        },
        {
            'data': [traces[1]],
            'layout': dict(xaxis={'type': 'log',
                                  'title': 'Frequency in Hz'},
                           yaxis={'title': 'Angle in degrees'},
                           margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                           legend={'x': 0, 'y': 1},
                           hovermode='closest',
                           transition={'duration': 500}
                           )
        },
        {
            'data': [traces[2]],
            'layout': dict(xaxis={'type': 'log',
                                  'title': 'Frequency in Hz'},
                           yaxis={'title': 'Group Delay in Samples'},
                           margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                           legend={'x': 0, 'y': 1},
                           hovermode='closest',
                           transition={'duration': 500}
                           )
        },
        pole_zero_fig,
        out_string
    ]


if __name__ == '__main__':
    app.run_server(debug=True)
