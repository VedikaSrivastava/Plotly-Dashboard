import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


result_df = pd.read_csv('Result.csv')
pa_assignment_df = pd.read_excel('PA_Assignment.xlsx')
pa_assignment_df['Billing_start_date'] = pd.to_datetime(pa_assignment_df['Billing_start_date'])
cohorts = result_df['Cohort_month'].unique()


app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Helper functions 
def create_line_chart(df, cohort):
    filtered_df = df[df['Cohort_month'] == cohort]
    fig = go.Figure(data=go.Scatter(x=filtered_df['Period'], y=filtered_df['User_count'], mode='lines+markers'))
    fig.update_layout(title=f'User Count Over Time for Cohort {cohort}', xaxis_title='Period', yaxis_title='User Count')
    # Add hover information and a grid
    fig.update_traces(hoverinfo='all', hovertemplate='Period: %{x}<br>User Count: %{y}')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    )
    fig.update_xaxes(tickangle=45)
    return fig

def create_heatmap(df):
    df['Cohort_month_formatted'] = pd.to_datetime(df['Cohort_month'], format='%B-%y')
    sorted_data = df.sort_values(by='Cohort_month_formatted')

    if 'Cohort_month_formatted' in sorted_data.columns and 'Period' in sorted_data.columns and 'User_count' in sorted_data.columns:
        heatmap_data = sorted_data.pivot(index='Cohort_month_formatted', columns='Period', values='User_count')
        fig = px.imshow(heatmap_data, labels=dict(x="Period", y="Cohort Month", color="User Count"), aspect="auto", color_continuous_scale=["lightblue", "blue"])
        fig.update_layout(title='User Retention Heatmap')
        fig.update_layout(coloraxis_colorbar=dict(title="User Count"))
        return fig
    else:
        raise ValueError("DataFrame does not contain the necessary columns to create a heatmap.")

def create_histogram(df):
    fig = px.histogram(df, x='Billing_amount', title='Billing Amount Distribution')
    fig.update_layout(xaxis_title='Billing Amount', yaxis_title='Count')
    fig.update_traces(marker_line_color='white', marker_line_width=1.5)
    fig.update_layout(
        bargap=0.2,
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    )
    return fig

def create_time_series(df):
    # Aggregate billing amount by month
    df['Billing_month'] = df['Billing_start_date'].dt.to_period('M')
    monthly_billing = df.groupby('Billing_month')['Billing_amount'].sum().reset_index()
    monthly_billing['Billing_month'] = monthly_billing['Billing_month'].dt.to_timestamp()
    fig = px.line(monthly_billing, x='Billing_month', y='Billing_amount', title='Total Billing Amount Over Time', markers=True)
    fig.update_layout(xaxis_title='Month', yaxis_title='Total Billing Amount')
    fig.update_traces(line_shape='spline', mode='lines+markers', marker=dict(size=5))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    )
    return fig

def create_user_engagement(df):
    engagement_over_time = df.groupby('Period')['User_count'].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=engagement_over_time['Period'],
        y=engagement_over_time['User_count'],
        mode='lines',
        name='User Engagement Over Time'
    ))
    fig.update_layout(
        title='User Engagement Over Time',
        xaxis_title='Period (Months since First Billing)',
        yaxis_title='Active User Count'
    )
    return fig

app.layout = html.Div([
    html.Div([
        html.Div('USER INSIGHTS', style={'textAlign': 'center', 'font-size': '30px', 'font-weight': 'bold', 'padding': '10px'})]),
    html.Div([
        html.Div('Select file:', style={'textAlign': 'center'}),
        dcc.RadioItems(
            id='file-selection',
            options=[
                {'label': 'Result.csv', 'value': 'result'},
                {'label': 'PA_Assignment.xlsx', 'value': 'pa_assignment'},
            ],
            value='result',
            labelStyle={'display': 'inline-block', 'padding': '5px'}
        ),
    ], style={'width': '100%', 'textAlign': 'center', 'padding': '20px', 'margin-bottom': '20px'}),
    html.Div(id='dynamic-content')  # Placeholder
])

@app.callback(
    Output('dynamic-content', 'children'),
    [Input('file-selection', 'value')]
)
def update_content(selected_file):
    if selected_file == 'result':
        content = html.Div([
            html.Div([
                dcc.Graph(figure=create_user_engagement(result_df), style={'display': 'inline-block', 'width': '50%'}),
                dcc.Graph(figure=create_heatmap(result_df), style={'display': 'inline-block', 'width': '50%'})     
            ], style={'display': 'flex'}),

            html.Div([
                    dcc.Slider(
                        id='cohort-selection',
                        min=0, max=len(cohorts) - 1, value=0,
                        marks={i: month for i, month in enumerate(cohorts)},
                        step=1,
                    ),
            dcc.Graph(id='line-chart', style={'padding': '5px'}),    
            ], style={'width': '50%', 'margin': 'auto', 'padding': '20px'}),
        ])
    else:
        content = html.Div([
            dcc.Graph(figure=create_histogram(pa_assignment_df), style={'width': '50%', 'display': 'inline-block'}),
            dcc.Graph(figure=create_time_series(pa_assignment_df), style={'width': '50%', 'display': 'inline-block'})
        ])
    return content

@app.callback(
    Output('line-chart', 'figure'),
    [Input('cohort-selection', 'value')]
)
def update_line_chart(selected_cohort):
    if selected_cohort is not None:
        return create_line_chart(result_df, cohorts[selected_cohort])


if __name__ == '__main__':
    app.run_server(debug=True)
