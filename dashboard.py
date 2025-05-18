import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Load data
df = pd.read_csv("ai_solutions_sales_data.csv")
df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour

# Categorize request types properly
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

# 1. Requests per hour with traffic zones
requests_per_hour = df['Hour'].value_counts().sort_index().reset_index()
requests_per_hour.columns = ['Hour', 'Count']

# 2. Job request pie chart (ALL valid job-related pages)
job_pages = ['/job.php', '/scheduledemo.php', '/aiassistant.php', '/event.php', '/prototype.php']
df_jobs = df[df['URL'].isin(job_pages)]
job_counts = df_jobs['URL'].value_counts().reset_index()
job_counts.columns = ['Job Page', 'Count']

# 3. Demo requests by country with suggestions
demo_by_country = df[df['RequestType'] == 'Scheduled Demo']['Country'].value_counts().reset_index()
demo_by_country.columns = ['Country', 'Demo Requests']
demo_by_country['Action'] = demo_by_country['Demo Requests'].apply(
    lambda x: "💡 Webinar" if x > 1000 else "📧 Email Campaign" if x > 500 else "📄 Translate Page"
)
demo_by_country['hover'] = demo_by_country.apply(
    lambda row: f"{row['Country']}<br>Requests: {row['Demo Requests']}<br>{row['Action']}", axis=1
)

# 4. Revenue by product
sales_by_product = df[df['Revenue'] > 0].groupby('Product').agg(
    TotalRevenue=('Revenue', 'sum'),
    AvgSale=('Revenue', 'mean')
).reset_index()
sales_by_product['Color'] = sales_by_product['AvgSale'].apply(
    lambda x: 'green' if x >= avg_sale_value else 'red'
)

# 5. Revenue by country
sales_by_country = df[df['Revenue'] > 0].groupby('Country').agg(
    TotalRevenue=('Revenue', 'sum'),
    AvgSale=('Revenue', 'mean')
).reset_index()

# 6. HTTP Status Codes
status_counts = df['Status'].value_counts().reset_index()
status_counts.columns = ['Status', 'Count']

# 7. Requests per country by type
type_country = df.groupby(['Country', 'RequestType']).size().reset_index(name='Count')

# App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def kpi_card(title, value, color):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title"),
            html.H3(value, className="card-text", style={"color": color})
        ]), className="m-2", style={"textAlign": "center"}
    )

app.layout = dbc.Container([
    html.H2("AI-Solutions Sales Dashboard", className="text-center my-4"),

    dbc.Row([
        dbc.Col(kpi_card("Total Requests", f"{total_requests:,}", "black"), width=3),
        dbc.Col(kpi_card("Total Revenue", f"${total_revenue:,.2f}", "green"), width=3),
        dbc.Col(kpi_card("Avg Sale Value", f"${avg_sale_value:,.2f}", "orange"), width=3),
        dbc.Col(kpi_card("Top Product", top_product, "blue"), width=3)
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("📊 Performance Gauge"),
            dcc.Graph(figure=go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=avg_sale_value,
                delta={'reference': 120},
                title={'text': "Average Sale Value ($)"},
                gauge={
                    'axis': {'range': [0, 200]},
                    'bar': {'color': "black"},
                    'steps': [
                        {'range': [0, 80], 'color': "#e74c3c"},
                        {'range': [80, 120], 'color': "#f39c12"},
                        {'range': [120, 200], 'color': "#2ecc71"}
                    ],
                    'threshold': {'line': {'color': "blue", 'width': 4}, 'value': 120}
                }
            )))
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Website Requests Per Hour"),
            dcc.Graph(figure=px.line(requests_per_hour, x='Hour', y='Count', markers=True,
                                     title="Hourly Traffic")
                      .add_vrect(x0=10, x1=14, fillcolor="green", opacity=0.15, annotation_text="Marketing")
                      .add_vrect(x0=9, x1=17, fillcolor="blue", opacity=0.08, annotation_text="Support")
                      .add_vrect(x0=1, x1=4, fillcolor="red", opacity=0.08, annotation_text="Maintenance"))
        ], width=6),
        dbc.Col([
            html.H5("Job-Related Requests"),
            dcc.Graph(figure=px.pie(job_counts, names='Job Page', values='Count', title="Job Service Usage"))
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Demo Requests by Country"),
            dcc.Graph(figure=px.bar(
                demo_by_country, x='Demo Requests', y='Country',
                hover_name='hover', text='Action', orientation='h',
                title="Demo Interest + Recommended Action"
            ).update_traces(marker_color='purple', textposition='outside'))
        ], width=6),
        dbc.Col([
            html.H5("Revenue by Product"),
            dcc.Graph(figure=px.bar(
                sales_by_product, x='Product', y='TotalRevenue', color='Color',
                title="Product Sales by Revenue",
                color_discrete_map={'green': 'green', 'red': 'red'}
            ))
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Revenue by Country"),
            dcc.Graph(figure=px.pie(
                sales_by_country, names='Country', values='TotalRevenue',
                title="Revenue Distribution by Country"
            ))
        ], width=6),
        dbc.Col([
            html.H5("HTTP Status Code Distribution"),
            dcc.Graph(figure=px.pie(status_counts, names='Status', values='Count',
                                    title="System Response Codes"))
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Request Types by Country"),
            dcc.Dropdown(id='country-dropdown',
                         options=[{'label': c, 'value': c} for c in sorted(df['Country'].unique())],
                         value='USA', clearable=False),
            dcc.Graph(id='requests-type-country')
        ])
    ])
], fluid=True)

@app.callback(
    Output('requests-type-country', 'figure'),
    Input('country-dropdown', 'value')
)
def update_request_type_chart(selected_country):
    filtered = type_country[type_country['Country'] == selected_country]
    fig = px.bar(filtered, x='RequestType', y='Count', color='RequestType',
                 title=f"Request Type Breakdown in {selected_country}")
    fig.update_layout(showlegend=False)
    return fig

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)

