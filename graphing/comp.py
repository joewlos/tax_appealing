# -*- coding: utf-8 -*-
'''
INITIALIZE
'''
# Import required packages
import json
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder

# Function for creating bar chart of comparable properties
def comp_graph(data):

	# Get the x and y values from the comparables
	x = ['Comparable {}'.format(z + 1) for z in range(len(data['comparable']))]
	y = sorted([int(z['match_tax_amount']) for z in data['comparable']], reverse=True)

	# Add the current property to the beginning of the lists
	x = ['Your Property'] + x
	y = [int(data['tax_amount'])] + y

	# Text includes "Tax Bill" for clarity
	text = ['${:,} Tax Bill'.format(i) for i in y]

	# Subject property has a different color, with rgba decreasing on each iteration
	colors = ['#384D48']
	color = 'rgba(112,61,87,'
	for i in range(len(data['comparable'])):
		new = color + '{})'.format(1.0 - i * 0.15)
		colors.append(new)

	# Create the bars
	bars = [
		go.Bar(
			x=x,
			y=y,
			name=x,
			text=text,
			hoverinfo='x+text',
			marker={'color': colors}
		)
	]

	# Provide the layout
	layout = go.Layout(
		showlegend=False,
		margin={
			't': 50,
			'r': 25,
			'pad': 5
		},
		xaxis={
			'title': 'This Address and Nearby Properties',
			'showgrid': False,
			'zeroline': False,
			'showline': False,
			'ticks': '',
			'showticklabels': False,
			'titlefont': {
				'family': '"Heebo", Helvetica, sans-serif',
				'size': 15
			}
		},
		yaxis={
			'title': 'Tax Bill',
			'showgrid': False,
			'zeroline': False,
			'showline': False,
			'ticks': '',
			'tickformat': ',d',
			'showticklabels': True,
			'tickprefix': '$',
			'range': [min(y) - (min(y) * 0.05), max(y) + (max(y) * 0.05)],
			'tickfont': {
				'family': '"Heebo", Helvetica, sans-serif',
				'size': 15
			},
			'titlefont': {
				'family': '"Heebo", Helvetica, sans-serif',
				'size': 15
			}
		},
		paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
		plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
		bargap=0.3
	)

	# Data as JSON for Plotly to render
	bars_json = json.dumps(bars, cls=PlotlyJSONEncoder)
	layout_json = json.dumps(layout, cls=PlotlyJSONEncoder)

	# Return both JSON strings
	return bars_json, layout_json