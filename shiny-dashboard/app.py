# Shinylive Dashboard Template
# A comprehensive 4-tab dashboard template for data science projects

from shiny import App, render, ui, reactive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

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
    cases = np.maximum(0, base_trend + seasonal + noise).astype(int)
    
    # Add some outbreak events
    outbreak_days = np.random.choice(n_days, 5, replace=False)
    for day in outbreak_days:
        cases[day:day+14] += np.random.poisson(30, min(14, n_days-day))
    
    time_series_data = pd.DataFrame({
        'date': dates,
        'cases': cases,
        'deaths': np.random.poisson(cases * 0.02),
        'hospitalizations': np.random.poisson(cases * 0.1),
        'tests': np.random.poisson(cases * 5),
        'positivity_rate': np.clip(cases / (cases * 5) * 100, 1, 25)
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
        'age_group': age_groups,
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
                    choices=["cases", "deaths", "hospitalizations", "positivity_rate"],
                    selected="cases"
                ),
                ui.br(),
                ui.h4("Key Statistics"),
                ui.output_ui("key_stats"),
                width=300
            ),
            ui.main_panel(
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
            ui.main_panel(
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
        )
    ),
    
    ui.nav_panel(
        "📈 Forecasting",
        ui.layout_sidebar(
            ui.sidebar(
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
                    choices=["cases", "deaths", "hospitalizations"],
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
            ui.main_panel(
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
                        ui.p("• Linear trend continuation"),
                        ui.p("• Historical variance patterns"),
                        ui.p("• No external intervention effects"),
                        ui.p("• Seasonal patterns maintained"),
                    ),
                    width=1/2
                )
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
        
        total = data[metric].sum() if metric != 'positivity_rate' else data[metric].mean()
        recent = data[metric].tail(7).mean()
        trend = "↗️" if recent > data[metric].head(7).mean() else "↘️"
        
        return ui.div(
            ui.p(f"Total: {total:,.1f}"),
            ui.p(f"7-day avg: {recent:.1f} {trend}"),
            ui.p(f"Days: {len(data)}")
        )
    
    @render.plot
    def trend_plot():
        """Main trend visualization"""
        data = filtered_data()
        metric = input.metric()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data['date'], data[metric], linewidth=2, alpha=0.8)
        
        # Add 7-day rolling average
        rolling_avg = data[metric].rolling(window=7, center=True).mean()
        ax.plot(data['date'], rolling_avg, linewidth=3, alpha=0.7, 
                label='7-day average', color='red')
        
        ax.set_title(f'{metric.replace("_", " ").title()} Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel(metric.replace("_", " ").title())
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    
    @render.plot
    def recent_performance():
        """Recent performance metrics"""
        data = filtered_data().tail(30)  # Last 30 days
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create a simple performance indicator
        metrics = ['cases', 'deaths', 'hospitalizations']
        values = [data[m].mean() for m in metrics]
        colors = plt.cm.viridis(np.linspace(0, 1, len(metrics)))
        
        bars = ax.bar(metrics, values, color=colors, alpha=0.7)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}', ha='center', va='bottom')
        
        ax.set_title('30-Day Average Metrics')
        ax.set_ylabel('Average Daily Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
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
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(regional_data['region'], regional_data['case_rate'], 
                     color=plt.cm.Set3(range(len(regional_data))))
        
        # Add value labels
        for bar, value in zip(bars, regional_data['case_rate']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}', ha='center', va='bottom')
        
        ax.set_title('Case Rates by Region (per 100K population)')
        ax.set_xlabel('Region')
        ax.set_ylabel('Cases per 100K')
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        return fig
    
    @render.plot
    def vax_capacity_plot():
        """Vaccination vs hospital capacity scatter plot"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        scatter = ax.scatter(regional_data['vaccination_rate'], 
                           regional_data['hospital_capacity'],
                           s=regional_data['total_cases']/50,  # Size by cases
                           c=regional_data['case_rate'],
                           cmap='RdYlBu_r',
                           alpha=0.7)
        
        # Add region labels
        for i, region in enumerate(regional_data['region']):
            ax.annotate(region, 
                       (regional_data['vaccination_rate'].iloc[i], 
                        regional_data['hospital_capacity'].iloc[i]),
                       xytext=(5, 5), textcoords='offset points')
        
        ax.set_xlabel('Vaccination Rate (%)')
        ax.set_ylabel('Hospital Capacity (%)')
        ax.set_title('Vaccination Rate vs Hospital Capacity\n(Size = Total Cases, Color = Case Rate)')
        
        plt.colorbar(scatter, label='Case Rate (per 100K)')
        plt.tight_layout()
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
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        values = age_data[metric].values
        if show_pct and metric != 'vaccinated':
            values = values / values.sum() * 100
            ylabel = f'{metric.title()} (%)'
        else:
            ylabel = metric.replace('_', ' ').title()
            if metric == 'vaccinated':
                ylabel += ' (%)'
        
        colors = plt.cm.plasma(np.linspace(0, 1, len(age_data)))
        bars = ax.bar(age_data['age_group'], values, color=colors, alpha=0.8)
        
        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}{"%" if show_pct or metric == "vaccinated" else ""}',
                   ha='center', va='bottom')
        
        ax.set_title(f'{metric.replace("_", " ").title()} by Age Group')
        ax.set_xlabel('Age Group')
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        return fig
    
    @render.plot
    def age_comparison():
        """Age group comparison radar/polar plot"""
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Normalize all metrics to 0-1 scale for comparison
        metrics = ['cases', 'deaths', 'vaccinated']
        angles = np.linspace(0, 2 * np.pi, len(age_data), endpoint=False)
        
        for i, metric in enumerate(metrics):
            values = age_data[metric].values
            normalized_values = (values - values.min()) / (values.max() - values.min())
            
            # Close the plot
            angles_plot = np.concatenate((angles, [angles[0]]))
            values_plot = np.concatenate((normalized_values, [normalized_values[0]]))
            
            ax.plot(angles_plot, values_plot, 'o-', linewidth=2, 
                   label=metric.replace('_', ' ').title(), alpha=0.7)
            ax.fill(angles_plot, values_plot, alpha=0.1)
        
        ax.set_xticks(angles)
        ax.set_xticklabels(age_data['age_group'])
        ax.set_ylim(0, 1)
        ax.set_title('Age Group Comparison\n(Normalized Values)', y=1.08)
        ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.tight_layout()
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
        z = np.polyfit(x, y, 1)
        trend = np.poly1d(z)
        
        # Generate forecast
        forecast_x = np.arange(len(recent_data), len(recent_data) + forecast_days)
        forecast_y = trend(forecast_x)
        
        # Add uncertainty (simple approach)
        residuals = y - trend(x)
        std_error = np.std(residuals)
        z_score = 1.96 if confidence == 95 else (2.58 if confidence == 99 else 1.64)
        
        upper_bound = forecast_y + z_score * std_error
        lower_bound = np.maximum(0, forecast_y - z_score * std_error)
        
        # Create forecast dates
        last_date = recent_data['date'].max()
        forecast_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                     periods=forecast_days, freq='D')
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Historical data
        ax.plot(recent_data['date'], recent_data[metric], 
               label='Historical', linewidth=2, color='blue')
        
        # Forecast
        ax.plot(forecast_dates, forecast_y, 
               label='Forecast', linewidth=2, color='red', linestyle='--')
        
        # Confidence interval
        ax.fill_between(forecast_dates, lower_bound, upper_bound, 
                       alpha=0.3, color='red', label=f'{confidence}% Confidence Interval')
        
        ax.axvline(x=last_date, color='gray', linestyle=':', alpha=0.7, 
                  label='Forecast Start')
        
        ax.set_title(f'{metric.replace("_", " ").title()} Forecast ({forecast_days} days)')
        ax.set_xlabel('Date')
        ax.set_ylabel(metric.replace("_", " ").title())
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
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
            ui.p(f"📈 Total period: {total_forecast:.0f}"),
            ui.p(f"🎯 Peak expected: Day {peak_day}"),
            ui.p(f"📅 Forecast period: {forecast_days} days"),
            ui.br(),
            ui.p("⚠️ This is a demonstration forecast. Production models would incorporate epidemiological parameters, interventions, and more sophisticated methods.",
                style="font-size: 0.9em; color: #666;")
        )

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
