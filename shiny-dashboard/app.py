# Shinylive Dashboard Template - Python Version
# A comprehensive 4-tab dashboard template for data science projects

from shiny import App, render, ui, reactive
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set global options for consistent styling
pd.set_option('display.float_format', '{:.1f}'.format)

# Generate sample data for the dashboard
def generate_sample_data():
    """Generate sample time series and categorical data for demonstration"""
    np.random.seed(42)
    
    # Time series data
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    n_days = len(dates)
    
    # Simulate epidemiological data with trends and seasonality
    base_trend = np.linspace(100, 150, n_days)
    seasonal = 20 * np.sin(2 * np.pi * np.arange(n_days) / 365.25)
    noise = np.random.normal(0, 10, n_days)
    cases = np.maximum(0, np.round(base_trend + seasonal + noise)).astype(int)
    
    # Add some outbreak events
    outbreak_days = np.random.choice(n_days, 5, replace=False)
    for day in outbreak_days:
        end_day = min(day + 14, n_days)
        outbreak_cases = np.random.poisson(30, end_day - day)
        cases[day:end_day] += outbreak_cases
    
    time_series_data = pd.DataFrame({
        'date': dates,
        'cases': cases,
        'deaths': np.random.poisson(np.maximum(1, cases * 0.02)),
        'hospitalizations': np.random.poisson(np.maximum(1, cases * 0.1)),
        'tests': np.random.poisson(np.maximum(1, cases * 5)),
        'positivity_rate': np.clip(cases / np.maximum(1, cases * 5) * 100, 1, 25)
    })
    
    # Regional data
    regions = ['North', 'South', 'East', 'West', 'Central']
    regional_data = pd.DataFrame({
        'region': regions,
        'population': [250000, 180000, 320000, 210000, 290000],
        'total_cases': np.random.poisson([5000, 3500, 6200, 4100, 5800]),
        'vaccination_rate': np.random.uniform(60, 85, 5),
        'hospital_capacity': np.random.uniform(70, 95, 5)
    })
    
    # Calculate rates per 100k
    regional_data['case_rate'] = (regional_data['total_cases'] / 
                                  regional_data['population'] * 100000).round(1)
    
    # Age group data
    age_groups = ['0-17', '18-34', '35-49', '50-64', '65+']
    age_data = pd.DataFrame({
        'age_group': pd.Categorical(age_groups, categories=age_groups, ordered=True),
        'cases': np.random.poisson([800, 1200, 1000, 900, 600]),
        'deaths': np.random.poisson([5, 15, 25, 40, 120]),
        'vaccinated': np.random.uniform([40, 70, 75, 80, 90], [60, 85, 90, 95, 98])
    })
    
    return time_series_data, regional_data, age_data

# Generate the sample data
time_series_data, regional_data, age_data = generate_sample_data()

# Define the UI
app_ui = ui.page_navbar(
    ui.nav_panel(
        "📊 Overview",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h3("Dashboard Controls"),
                ui.input_date_range(
                    "date_range",
                    "Select Date Range:",
                    start=time_series_data['date'].min(),
                    end=time_series_data['date'].max(),
                    min=time_series_data['date'].min(),
                    max=time_series_data['date'].max()
                ),
                ui.input_select(
                    "metric",
                    "Primary Metric:",
                    choices={
                        "cases": "Cases", 
                        "deaths": "Deaths", 
                        "hospitalizations": "Hospitalizations", 
                        "positivity_rate": "Positivity Rate"
                    },
                    selected="cases"
                ),
                ui.br(),
                ui.h4("Key Statistics"),
                ui.output_ui("key_stats"),
                width=300
            ),
            ui.h2("Data Science Dashboard Template"),
            ui.p("This dashboard demonstrates common patterns for data science deliverables, "
                 "including time series visualization, regional comparisons, and demographic analysis."),
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header("📈 Trend Analysis"),
                    ui.output_plot("trend_plot"),
                ),
                ui.card(
                    ui.card_header("🎯 Recent Performance"),
                    ui.output_plot("recent_performance"),
                ),
                width=1/2
            ),
            ui.card(
                ui.card_header("📋 Data Summary"),
                ui.output_data_frame("summary_table")
            )
        )
    ),
    
    ui.nav_panel(
        "🗺️ Regional Analysis",
        ui.layout_column_wrap(
            ui.card(
                ui.card_header("Regional Case Rates (per 100K population)"),
                ui.output_plot("regional_cases_plot"),
            ),
            ui.card(
                ui.card_header("Vaccination vs Hospital Capacity"),
                ui.output_plot("vax_capacity_plot"),
            ),
            width=1/2
        ),
        ui.card(
            ui.card_header("Regional Comparison Table"),
            ui.output_data_frame("regional_table")
        )
    ),
    
    ui.nav_panel(
        "👥 Demographics",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h4("Display Options"),
                ui.input_radio_buttons(
                    "demo_metric",
                    "Select Metric:",
                    choices={
                        "cases": "Cases",
                        "deaths": "Deaths", 
                        "vaccinated": "Vaccination Rate"
                    },
                    selected="cases"
                ),
                ui.input_checkbox(
                    "show_percentages",
                    "Show as percentages",
                    value=False
                ),
                width=250
            ),
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header("Age Group Distribution"),
                    ui.output_plot("age_distribution"),
                ),
                ui.card(
                    ui.card_header("Age Group Comparison"),
                    ui.output_plot("age_comparison"),
                ),
                width=1/2
            ),
            ui.card(
                ui.card_header("Demographic Summary"),
                ui.output_data_frame("demo_table")
            )
        )
    ),
    
    ui.nav_panel(
        "📈 Forecasting",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h4("Forecast Parameters"),
                ui.input_slider(
                    "forecast_days",
                    "Forecast Period (days):",
                    min=7,
                    max=90,
                    value=30,
                    step=7
                ),
                ui.input_select(
                    "forecast_metric",
                    "Forecast Metric:",
                    choices={
                        "cases": "Cases", 
                        "deaths": "Deaths", 
                        "hospitalizations": "Hospitalizations"
                    },
                    selected="cases"
                ),
                ui.input_slider(
                    "confidence_level",
                    "Confidence Level:",
                    min=80,
                    max=99,
                    value=95,
                    step=5,
                    post="%"
                ),
                ui.br(),
                ui.h4("Model Information"),
                ui.p("Simple trend-based forecast for demonstration purposes. "
                     "Production models would use more sophisticated methods."),
                width=280
            ),
            ui.card(
                ui.card_header("📊 Forecast Visualization"),
                ui.output_plot("forecast_plot"),
            ),
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header("🎯 Forecast Summary"),
                    ui.output_ui("forecast_summary"),
                ),
                ui.card(
                    ui.card_header("⚠️ Model Assumptions"),
                    ui.tags.ul(
                        ui.tags.li("Linear trend continuation"),
                        ui.tags.li("Historical variance patterns"),
                        ui.tags.li("No external intervention effects"),
                        ui.tags.li("Seasonal patterns maintained")
                    )
                ),
                width=1/2
            )
        )
    ),
    
    title="Data Science Dashboard",
    id="navbar"
)

# Define server logic
def server(input, output, session):
    
    @reactive.calc
    def filtered_data():
        """Filter time series data based on date range"""
        start_date = pd.to_datetime(input.date_range()[0])
        end_date = pd.to_datetime(input.date_range()[1])
        return time_series_data[
            (time_series_data['date'] >= start_date) & 
            (time_series_data['date'] <= end_date)
        ]
    
    @render.ui
    def key_stats():
        """Generate key statistics for sidebar"""
        data = filtered_data()
        metric = input.metric()
        
        if metric == 'positivity_rate':
            total = f"{data[metric].mean():.1f}%"
        else:
            total = f"{data[metric].sum():,.0f}"
        
        recent = data[metric].tail(7).mean()
        trend = "↗️" if recent > data[metric].head(7).mean() else "↘️"
        
        return ui.div(
            ui.p(f"Total: {total}"),
            ui.p(f"7-day avg: {recent:.1f} {trend}"),
            ui.p(f"Days: {len(data)}")
        )
    
    @render.plot
    def trend_plot():
        """Main trend visualization"""
        data = filtered_data()
        metric = input.metric()
        
        # Calculate 7-day rolling average
        rolling_avg = data[metric].rolling(window=7, center=True).mean()
        
        fig = go.Figure()
        
        # Add main trend line
        fig.add_trace(go.Scatter(
            x=data['date'], 
            y=data[metric],
            mode='lines',
            name=metric.replace('_', ' ').title(),
            line=dict(color='steelblue', width=2),
            opacity=0.6
        ))
        
        # Add rolling average
        fig.add_trace(go.Scatter(
            x=data['date'], 
            y=rolling_avg,
            mode='lines',
            name='7-day Average',
            line=dict(color='red', width=3),
            opacity=0.8
        ))
        
        fig.update_layout(
            title=f'{metric.replace("_", " ").title()} Over Time',
            xaxis_title="Date",
            yaxis_title=metric.replace("_", " ").title(),
            hovermode='x unified'
        )
        
        return fig
    
    @render.plot
    def recent_performance():
        """Recent performance metrics"""
        data = filtered_data().tail(30)  # Last 30 days
        
        metrics = ['Cases', 'Deaths', 'Hospitalizations']
        values = [
            data['cases'].mean(),
            data['deaths'].mean(),
            data['hospitalizations'].mean()
        ]
        
        fig = go.Figure(data=[
            go.Bar(x=metrics, y=values, 
                   text=[f'{v:.1f}' for v in values],
                   textposition='outside',
                   marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        ])
        
        fig.update_layout(
            title='30-Day Average Metrics',
            xaxis_title='Metric',
            yaxis_title='Average Daily Count',
            showlegend=False
        )
        
        return fig
    
    @render.data_frame
    def summary_table():
        """Summary statistics table"""
        data = filtered_data()
        
        summary = pd.DataFrame({
            'Metric': ['Cases', 'Deaths', 'Hospitalizations', 'Positivity Rate'],
            'Total/Average': [
                f"{data['cases'].sum():,}",
                f"{data['deaths'].sum():,}",
                f"{data['hospitalizations'].sum():,}",
                f"{data['positivity_rate'].mean():.1f}%"
            ],
            'Daily Average': [
                f"{data['cases'].mean():.1f}",
                f"{data['deaths'].mean():.1f}",
                f"{data['hospitalizations'].mean():.1f}",
                f"{data['positivity_rate'].mean():.1f}%"
            ],
            'Peak Value': [
                f"{data['cases'].max():,}",
                f"{data['deaths'].max():,}",
                f"{data['hospitalizations'].max():,}",
                f"{data['positivity_rate'].max():.1f}%"
            ]
        })
        
        return render.DataGrid(summary, width="100%")
    
    @render.plot
    def regional_cases_plot():
        """Regional case rates visualization"""
        fig = go.Figure(data=[
            go.Bar(x=regional_data['region'], 
                   y=regional_data['case_rate'],
                   text=regional_data['case_rate'].round(1),
                   textposition='outside',
                   marker_color=px.colors.qualitative.Set3[:len(regional_data)])
        ])
        
        fig.update_layout(
            title='Case Rates by Region (per 100K population)',
            xaxis_title='Region',
            yaxis_title='Cases per 100K',
            showlegend=False
        )
        
        return fig
    
    @render.plot
    def vax_capacity_plot():
        """Vaccination vs hospital capacity scatter plot"""
        fig = go.Figure(data=go.Scatter(
            x=regional_data['vaccination_rate'],
            y=regional_data['hospital_capacity'],
            mode='markers',
            marker=dict(
                size=regional_data['total_cases']/50,
                color=regional_data['case_rate'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Case Rate")
            ),
            text=regional_data['region'],
            hovertemplate=(
                "Region: %{text}<br>" +
                "Vaccination Rate: %{x:.1f}%<br>" +
                "Hospital Capacity: %{y:.1f}%<br>" +
                "Total Cases: %{marker.size}<br>" +
                "Case Rate: %{marker.color:.1f}<extra></extra>"
            )
        ))
        
        fig.update_layout(
            title='Vaccination Rate vs Hospital Capacity<br><sub>Size = Total Cases, Color = Case Rate</sub>',
            xaxis_title='Vaccination Rate (%)',
            yaxis_title='Hospital Capacity (%)'
        )
        
        return fig
    
    @render.data_frame
    def regional_table():
        """Regional comparison table"""
        display_data = regional_data.copy()
        display_data['vaccination_rate'] = display_data['vaccination_rate'].round(1)
        display_data['hospital_capacity'] = display_data['hospital_capacity'].round(1)
        display_data['population'] = display_data['population'].apply(lambda x: f"{x:,}")
        display_data['total_cases'] = display_data['total_cases'].apply(lambda x: f"{x:,}")
        
        return render.DataGrid(display_data, width="100%")
    
    @render.plot
    def age_distribution():
        """Age group distribution plot"""
        metric = input.demo_metric()
        show_pct = input.show_percentages()
        
        values = age_data[metric].values
        
        if show_pct and metric != "vaccinated":
            values = values / values.sum() * 100
            ylabel = f'{metric.title()} (%)'
        else:
            ylabel = metric.title()
            if metric == "vaccinated":
                ylabel += " (%)"
        
        text_values = [f'{v:.1f}{"%" if show_pct or metric == "vaccinated" else ""}' 
                      for v in values]
        
        fig = go.Figure(data=[
            go.Bar(x=age_data['age_group'], 
                   y=values,
                   text=text_values,
                   textposition='outside',
                   marker_color=px.colors.sequential.Plasma[:len(age_data)])
        ])
        
        fig.update_layout(
            title=f'{metric.replace("_", " ").title()} by Age Group',
            xaxis_title='Age Group',
            yaxis_title=ylabel,
            showlegend=False
        )
        
        return fig
    
    @render.plot
    def age_comparison():
        """Age group comparison radar/polar plot"""
        # Normalize all metrics to 0-1 scale for comparison
        norm_data = age_data.copy()
        for col in ['cases', 'deaths', 'vaccinated']:
            norm_data[f'{col}_norm'] = ((norm_data[col] - norm_data[col].min()) / 
                                      (norm_data[col].max() - norm_data[col].min()))
        
        # Create radar chart using scatterpolar
        fig = go.Figure()
        
        # Add traces for each metric
        metrics = [
            ('cases_norm', 'Cases', 'blue'),
            ('deaths_norm', 'Deaths', 'red'),
            ('vaccinated_norm', 'Vaccinated', 'green')
        ]
        
        for metric, name, color in metrics:
            # Close the plot by adding first value at the end
            values = list(norm_data[metric]) + [norm_data[metric].iloc[0]]
            categories = list(norm_data['age_group']) + [norm_data['age_group'].iloc[0]]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                fillcolor=f'rgba({{"blue": "0,0,255", "red": "255,0,0", "green": "0,255,0"}}[color],0.1)',
                name=name,
                line=dict(color=color)
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            title='Age Group Comparison<br><sub>Normalized Values</sub>',
            legend=dict(orientation="h", x=0.5, xanchor='center')
        )
        
        return fig
    
    @render.data_frame
    def demo_table():
        """Demographics summary table"""
        display_data = age_data.copy()
        display_data['vaccinated'] = display_data['vaccinated'].round(1)
        display_data['case_fatality_rate'] = (
            (display_data['deaths'] / display_data['cases'] * 100).round(2)
        )
        
        return render.DataGrid(display_data, width="100%")
    
    @render.plot
    def forecast_plot():
        """Generate forecast visualization"""
        metric = input.forecast_metric()
        forecast_days = input.forecast_days()
        confidence = input.confidence_level()
        
        # Use recent data for forecast
        recent_data = time_series_data.tail(90)
        
        # Simple linear trend forecast (for demonstration)
        x = np.arange(len(recent_data))
        y = recent_data[metric].values
        
        # Fit linear trend
        coeffs = np.polyfit(x, y, 1)
        trend_line = np.poly1d(coeffs)
        
        # Generate forecast
        forecast_x = np.arange(len(recent_data), len(recent_data) + forecast_days)
        forecast_y = trend_line(forecast_x)
        
        # Add uncertainty (simple approach)
        residuals = y - trend_line(x)
        std_error = np.std(residuals)
        z_score = {95: 1.96, 99: 2.58, 80: 1.64, 85: 1.44, 90: 1.64}[confidence]
        
        upper_bound = forecast_y + z_score * std_error
        lower_bound = np.maximum(0, forecast_y - z_score * std_error)
        
        # Create forecast dates
        last_date = recent_data['date'].max()
        forecast_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                     periods=forecast_days, freq='D')
        
        # Create the plot
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=recent_data['date'], 
            y=recent_data[metric],
            mode='lines',
            name='Historical',
            line=dict(color='blue', width=2)
        ))
        
        # Forecast line
        fig.add_trace(go.Scatter(
            x=forecast_dates, 
            y=forecast_y,
            mode='lines',
            name='Forecast',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=list(forecast_dates) + list(forecast_dates[::-1]),
            y=list(upper_bound) + list(lower_bound[::-1]),
            fill='toself',
            fillcolor='rgba(255,0,0,0.3)',
            line=dict(color='rgba(255,255,255,0)'),
            name=f'{confidence}% Confidence Interval'
        ))
        
        # Forecast start line
        fig.add_vline(
            x=last_date,
            line=dict(color='gray', dash='dot', width=1),
            annotation=dict(text="Forecast Start", showarrow=False)
        )
        
        fig.update_layout(
            title=f'{metric.replace("_", " ").title()} Forecast ({forecast_days} days)',
            xaxis_title='Date',
            yaxis_title=metric.replace("_", " ").title(),
            hovermode='x unified'
        )
        
        return fig
    
    @render.ui
    def forecast_summary():
        """Forecast summary statistics"""
        metric = input.forecast_metric()
        forecast_days = input.forecast_days()
        
        # Simple calculations for demo
        recent_avg = time_series_data[metric].tail(7).mean()
        
        # Mock forecast statistics
        forecast_avg = recent_avg * 1.05  # Slight increase
        total_forecast = forecast_avg * forecast_days
        peak_day = np.random.randint(7, forecast_days)
        
        return ui.div(
            ui.h4("Forecast Highlights"),
            ui.p(f"📊 Average daily: {forecast_avg:.1f}"),
            ui.p(f"📈 Total period: {total_forecast:,.0f}"),
            ui.p(f"🎯 Peak expected: Day {peak_day}"),
            ui.p(f"📅 Forecast period: {forecast_days} days"),
            ui.br(),
            ui.p("⚠️ This is a demonstration forecast. Production models would incorporate "
                 "epidemiological parameters, interventions, and more sophisticated methods.",
                style="font-size: 0.9em; color: #666;")
        )

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
