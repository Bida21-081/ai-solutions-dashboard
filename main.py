import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Load data
df = pd.read_csv("ai_solutions_sales_data.csv")
df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour

# Categorize request type
df['RequestType'] = df['URL'].apply(lambda x: 'AI Assistant' if x == '/aiassistant.php'
                                    else 'Scheduled Demo' if x == '/scheduledemo.php'
                                    else 'Promotional Event' if x == '/event.php'
                                    else 'Job Request' if x in ['/job.php', '/prototype.php']
                                    else 'Other')

# Metrics
total_requests = len(df)
total_revenue = df['Revenue'].sum()
avg_sale_value = df[df['Revenue'] > 0]['Revenue'].mean()
top_product = df[df['Revenue'] > 0]['Product'].value_counts().idxmax()

# Aggregated Data
requests_per_hour = df['Hour'].value_counts().sort_index().reset_index()
requests_per_hour.columns = ['Hour', 'Count']

job_counts = df[df['RequestType'] == 'Job Request']['URL'].value_counts().reset_index()
job_counts.columns = ['Job Page', 'Count']

demo_by_country = df[df['RequestType'] == 'Scheduled Demo']['Country'].value_counts().reset_index()
demo_by_country.columns = ['Country', 'Demo Requests']

# Sales by product with average sale and color coding
sales_by_product = df[df['Revenue'] > 0].groupby('Product').agg(
    TotalRevenue=('Revenue', 'sum'),
    CountSales=('Revenue', 'count'),
    AvgSaleValue=('Revenue', 'mean')
).reset_index()

sales_by_product['Color'] = sales_by_product['AvgSaleValue'].apply(
    lambda x: 'green' if x >= avg_sale_value else 'red'
)

# Sales by country with average sale per country
sales_by_country = df[df['Revenue'] > 0].groupby('Country').agg(
    TotalRevenue=('Revenue', 'sum'),
    CountSales=('Revenue', 'count'),
    AvgSaleValue=('Revenue', 'mean')
).reset_index()

# Add hover text for sales by country
sales_by_country['hover_text'] = sales_by_country.apply(
    lambda row: f"{row['Country']}<br>Total Revenue: ${row['TotalRevenue']:,.2f}<br>Avg Sale: ${row['AvgSaleValue']:,.2f}",
    axis=1
)

# Request types by country
type_country = df.groupby(['Country', 'RequestType']).size().reset_index(name='Count')

# HTTP Status counts fix
status_counts = df['Status'].value_counts().reset_index()
status_counts.columns = ['Status', 'Count']

# App setup
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "AI-Solutions Dashboard"

def kpi_card(title, value, color="primary"):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title"),
            html.H3(value, className="card-text", style={"color": color})
        ]),
        className="m-2 shadow-sm",
        style={"textAlign": "center"}
    )

app.layout = dbc.Container([
    html.H1("🧠 AI-Solutions Interactive Dashboard", className="text-center my-4"),

    dbc.Row([
        dbc.Col(kpi_card("Total Requests", f"{total_requests:,}", "dark"), width=3),
        dbc.Col(kpi_card("Total Revenue ($)", f"${total_revenue:,.2f}", "success"), width=3),
        dbc.Col(kpi_card("Avg Sale Value ($)", f"${avg_sale_value:,.2f}", "warning"), width=3),
        dbc.Col(kpi_card("Top Product", top_product, "info"), width=3)
    ], justify="center"),

    dbc.Row([
        dbc.Col([
            html.H5("🎯 Performance Gauge: Avg Sale Value", className="text-center mb-3"),
            dcc.Graph(figure=go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=avg_sale_value,
                delta={'reference': 120, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                title={'text': "Average Sale Value ($)", 'font': {'size': 18}},
                gauge={
                    'axis': {'range': [0, 200]},
                    'bar': {'color': "black"},
                    'steps': [
                        {'range': [0, 80], 'color': "#e74c3c"},
                        {'range': [80, 120], 'color': "#f39c12"},
                        {'range': [120, 200], 'color': "#2ecc71"},
                    ],
                    'threshold': {
                        'line': {'color': "blue", 'width': 4},
                        'thickness': 0.75,
                        'value': 120
                    }
                }
            )).update_layout(margin=dict(l=30, r=30, t=30, b=30), height=300))
        ], width=6)
    ], justify="center"),

    dbc.Row([
        dbc.Col([
            html.H5("Requests by Hour", className="mt-4"),
            dcc.Graph(figure=px.line(requests_per_hour, x='Hour', y='Count', markers=True,
                                     title="Hourly Web Traffic"))
        ], width=6),
        dbc.Col([
            html.H5("Job-Related Requests", className="mt-4"),
            dcc.Graph(figure=px.pie(job_counts, names='Job Page', values='Count',
                                    title="Job Page Distribution"))
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Demo Requests by Country", className="mt-4"),
            dcc.Graph(figure=px.bar(demo_by_country, x='Demo Requests', y='Country', orientation='h',
                                    title="Scheduled Demo Requests"))
        ], width=6),
        dbc.Col([
            html.H5("Revenue by Product", className="mt-4"),
            dcc.Graph(figure=px.bar(
                sales_by_product,
                x='Product',
                y='TotalRevenue',
                color='Color',
                title="Product Revenue with Avg Sale Value Indicator",
                labels={'TotalRevenue': 'Total Revenue ($)', 'Product': 'Product'},
                color_discrete_map={'green': 'green', 'red': 'red'}
            ))
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Sales by Country", className="mt-4"),
            dcc.Graph(figure=px.pie(
                sales_by_country,
                names='Country',
                values='TotalRevenue',
                title="Revenue Distribution by Country",
                hover_data=['AvgSaleValue'],
                hover_name='hover_text'
            ))
        ], width=6),
        dbc.Col([
            html.H5("HTTP Status Codes", className="mt-4"),
            dcc.Graph(figure=px.pie(status_counts, names='Status', values='Count',
                                    title="System Response Codes"))
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Request Types per Country", className="mt-4"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(df['Country'].unique())],
                value='USA',
                clearable=False
            ),
            dcc.Graph(id='requests-type-country')
        ], width=12)
    ])
], fluid=True)


@app.callback(
    Output('requests-type-country', 'figure'),
    Input('country-dropdown', 'value')
)
def update_request_type_chart(selected_country):
    filtered = type_country[type_country['Country'] == selected_country]
    fig = px.bar(filtered, x='RequestType', y='Count', color='RequestType',
                 title=f"Request Types Breakdown for {selected_country}",
                 labels={'Count': 'Number of Requests', 'RequestType': 'Request Type'})
    fig.update_layout(showlegend=False)
    return fig


import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))  # Get the PORT from Render's environment
    app.run(host="0.0.0.0", port=port, debug=True)

