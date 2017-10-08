# -*- coding: utf-8 -*-
import requests
import calendar
from datetime import datetime
from collections import defaultdict
import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go	

# initialize app 
app = dash.Dash()

#function from plotly example useful for parsing pandas dataframe into dash table.
def make_weather_table( dtf):
    ''' Return a dash definitio of an HTML table for a Pandas dataframe '''
    table =[0,html.Tr([
						html.Th(['Day']),html.Th(['Description']),html.Th(['Humidyty']),html.Th(['Temperature']),html.Th(['Wind'])
					])]
    for index, row in dtf.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append( html.Td([ row[i] ]) )
        table.append( html.Tr( html_row ) )

    return table
#openweather api call returns pandas dataframe 
def api_call(input_value="Ames,us"):
	city = input_value.replace(" ", "").split(" ")[0]
	state = 'us'
	r = requests.get("http://api.openweathermap.org/data/2.5/forecast?q={},{}&appid=1a5f1a13b6a17aad19b3663428ad26e9".format(city,state))
	data = r.json()

	day = [calendar.day_name[(datetime.strptime(data["list"][i]['dt_txt'].split(" ")[0],'%Y-%M-%d')).weekday()] for i in range(3,36,8)]
	description = [data["list"][i]["weather"][0]['description'] for i in range(3,36,8)]
	temp = [round(data["list"][i]['main']['temp'] * (9/5) - 459.67) for i in range(3,36,8)]
	wind_speed = [data["list"][i]['wind']['speed'] for i in range(3,36,8)]
	humidity = [data["list"][i]['main']['humidity'] for i in range(3,36,8)]
	df = pd.DataFrame(data={'Day':day,'Description':description,'Temperature':temp,'Humidity':humidity,'Wind':wind_speed})
	
	return df

# UI layout 
app.layout = html.Div([

#header
	html.Div([
		html.H1('Weather Forcast with PlotlyDash and OpenWeatherMapApi', style={'font-family': 'Dosis','font-size': '4.0rem','textAlign': 'center'})
	    ]),

#input 
    html.Div([
    	html.P("Enter City and country code or just city"),
    	html.Div([dcc.Input(id='city_name',  placeholder="ex Ames,usa", value="Ames,usa", type = "text")
    		])
    	]),   

#output
	html.Div([
    	html.Div(id='city_id')
    	]),

	# html.Br(),

	html.Div([
		dcc.Graph(id="weather_graph",
			style=dict(width='700px'))
		])#,

	# html.Div([
	# html.Table(make_weather_table(api_call()))
	# ])
    

], className='container')

@app.callback(
	Output(component_id='city_id', component_property='children'),
	[Input(component_id='city_name', component_property='value')]
)

#function to update the app
def update_weather(input_value):
	icons =  {"snow":"https://ssl.gstatic.com/onebox/weather/64/snow.png","cloud":"https://ssl.gstatic.com/onebox/weather/64/cloudy.png",
				"rain":"https://ssl.gstatic.com/onebox/weather/64/rain.png","sunny":"https://ssl.gstatic.com/onebox/weather/64/sunny.png",
				"fog":"https://ssl.gstatic.com/onebox/weather/64/fog.png"}
	df = api_call(input_value)	

	temp_icon = ["http://nwas.org/wp-content/uploads/2011/07/Weather-Brains-300x169.jpg"]
	for key, value in icons.items():
		if key in df.Description[0]:
					temp_icon = icons[key]
	
	input_value = input_value 

	app.layout = html.Div([

		html.H3(input_value,style={"color":'#878787'}),
			html.P(df.Day[0],style={'fontSize':'20px'}),
			html.P(df.Description[0],style={'fontSize':'18px'}),

			html.Div(style={'height': '64px','display':'inline','position': 'relative','width': '64px','margin-top':'-9px'},children = [
						html.Img(src=temp_icon[0]),
						html.P("{}F".format(df.Temperature[0]),style={'fontSize':'36px','display':'inline'})
						]),
			
			html.Div(style={"float":"right",'fontSize':'20px'},children=[
				html.P("Humidity: {}%".format(df.Humidity[0])),
				html.P("Wind: {} mph".format(df.Wind[0]))
			]),

			html.Div(children=[
			dcc.Graph(
		        id='weather_graph',
		         figure=go.Figure(
			        data=[
			            go.Scatter(x=list(df.Day), y=list(df.Temperature), mode='lines+markers',name="temperature"),
			            go.Scatter(x=list(df.Day), y=list(df.Humidity), mode='lines+markers',name='Humidity'),
			            go.Scatter(x=list(df.Day), y=list(df.Wind), mode='lines+markers',name='wind')
			        ],
			        layout=go.Layout(
			            title='Five Day Weather Forcast For {}'.format(input_value),
			            showlegend=True,
			            margin=go.Margin(l=20, r=0, t=40, b=20)
			        
		        	)
		        ))

		        ]),

			html.Div([
				html.Br(),
				html.Hr(),
				html.P("Table for {} Weather Information".format(input_value), style={"textAlign":"center"}),
				html.Table(
					),
				html.Table(
					make_weather_table(df)
				)

				])


		])

	return(app.layout)

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/0e463810ed36927caf20372b6411690692f94819/dash-drug-discovery-demo-stylesheet.css"]


for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
	app.run_server(port=8080,debug=True)