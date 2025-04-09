# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get the list of unique launch sites from the dataset
launch_sites = spacex_df['Launch Site'].unique()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Dropdown for Launch Site selection
                                html.Div([
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[
                                            {'label': 'All Sites', 'value': 'ALL'}] +  # 'ALL' option to show data for all sites
                                            [{'label': site, 'value': site} for site in launch_sites],  # Each launch site in the dropdown
                                        value='ALL',  # Default is 'ALL'
                                        placeholder="Select a Launch Site here",
                                        searchable=True
                                    )
                                ], style={'width': '48%', 'padding': '20px', 'display': 'inline-block'}),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                # TASK 3: Add a slider to select payload range
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, 
                                    max=10000, 
                                    step=1000,
                                    marks={i: str(i) for i in range(0, 10001, 1000)},  # Marks every 1000kg
                                    value=[min_payload, max_payload]  # Set initial range to the min and max payload
                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(
                                    dcc.Graph(id='success-payload-scatter-chart')),
                                ]),


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        # For all sites, show the success vs failure counts
        success_counts = spacex_df.groupby('class').size()
        fig = px.pie(
            values=success_counts, 
            names=['Failure', 'Success'], 
            title='Launch Success vs Failure for All Sites'
        )
    else:
        # Filter the data for the selected site
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = site_data.groupby('class').size()
        fig = px.pie(
            values=success_counts, 
            names=['Failure', 'Success'], 
            title=f"Launch Success vs Failure for {selected_site}"
        )
    
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_plot(selected_site, payload_range):
    min_payload, max_payload = payload_range
    
    # Filter the dataframe based on the payload range
    filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & 
                              (spacex_df['Payload Mass (kg)'] <= max_payload)]
    
    if selected_site != 'ALL':
        # Filter further by the selected launch site
        filtered_data = filtered_data[filtered_data['Launch Site'] == selected_site]
    
    # Create a scatter plot for Payload vs. Success
    fig = px.scatter(
        filtered_data, 
        x='Payload Mass (kg)', 
        y='class', 
        color='class', 
        title=f"Payload vs Launch Success for {selected_site}" if selected_site != 'ALL' else 'Payload vs Launch Success for All Sites',
        labels={'class': 'Launch Success (1=Success, 0=Failure)', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        color_continuous_scale='Viridis'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
