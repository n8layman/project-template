# Shinylive Dashboard Template - R Version
# A comprehensive 4-tab dashboard template for data science projects

library(shiny)
library(bslib)
library(dplyr)
library(plotly)
library(DT)
library(lubridate)
library(scales)
library(RColorBrewer)
library(zoo)  # For rollmean function

# Set global options for consistent styling
options(scipen = 999)  # Avoid scientific notation

# Generate sample data for the dashboard
generate_sample_data <- function() {
  """Generate sample time series and categorical data for demonstration"""
  set.seed(42)
  
  # Time series data
  dates <- seq(as.Date("2023-01-01"), as.Date("2024-12-31"), by = "day")
  n_days <- length(dates)
  
  # Simulate epidemiological data with trends and seasonality
  base_trend <- seq(100, 150, length.out = n_days)
  seasonal <- 20 * sin(2 * pi * seq_along(dates) / 365.25)
  noise <- rnorm(n_days, 0, 10)
  cases <- pmax(0, round(base_trend + seasonal + noise))
  
  # Add some outbreak events
  outbreak_days <- sample(n_days, 5)
  for (day in outbreak_days) {
    end_day <- min(day + 13, n_days)
    outbreak_cases <- rpois(length(day:end_day), 30)
    cases[day:end_day] <- cases[day:end_day] + outbreak_cases
  }
  
  time_series_data <- data.frame(
    date = dates,
    cases = cases,
    deaths = rpois(n_days, pmax(1, cases * 0.02)),
    hospitalizations = rpois(n_days, pmax(1, cases * 0.1)),
    tests = rpois(n_days, pmax(1, cases * 5)),
    positivity_rate = pmax(1, pmin(25, cases / pmax(1, cases * 5) * 100))
  )
  
  # Regional data
  regions <- c('North', 'South', 'East', 'West', 'Central')
  regional_data <- data.frame(
    region = regions,
    population = c(250000, 180000, 320000, 210000, 290000),
    total_cases = rpois(5, c(5000, 3500, 6200, 4100, 5800)),
    vaccination_rate = runif(5, 60, 85),
    hospital_capacity = runif(5, 70, 95)
  ) %>%
    mutate(case_rate = round(total_cases / population * 100000, 1))
  
  # Age group data
  age_groups <- c('0-17', '18-34', '35-49', '50-64', '65+')
  age_data <- data.frame(
    age_group = factor(age_groups, levels = age_groups),
    cases = rpois(5, c(800, 1200, 1000, 900, 600)),
    deaths = rpois(5, c(5, 15, 25, 40, 120)),
    vaccinated = runif(5, c(40, 70, 75, 80, 90), c(60, 85, 90, 95, 98))
  )
  
  list(
    time_series = time_series_data,
    regional = regional_data,
    age = age_data
  )
}

# Generate the sample data
sample_data <- generate_sample_data()

# Define UI
ui <- page_navbar(
  title = "Data Science Dashboard",
  id = "navbar",
  theme = bs_theme(version = 5, bootswatch = "flatly"),
  
  # Overview Tab
  nav_panel(
    title = "📊 Overview",
    layout_sidebar(
      sidebar = sidebar(
        title = "Dashboard Controls",
        width = 300,
        dateRangeInput(
          "date_range",
          "Select Date Range:",
          start = min(sample_data$time_series$date),
          end = max(sample_data$time_series$date),
          min = min(sample_data$time_series$date),
          max = max(sample_data$time_series$date)
        ),
        selectInput(
          "metric",
          "Primary Metric:",
          choices = c("Cases" = "cases", 
                     "Deaths" = "deaths", 
                     "Hospitalizations" = "hospitalizations", 
                     "Positivity Rate" = "positivity_rate"),
          selected = "cases"
        ),
        br(),
        h4("Key Statistics"),
        uiOutput("key_stats")
      ),
      
      h2("Data Science Dashboard Template"),
      p("This dashboard demonstrates common patterns for data science deliverables, 
        including time series visualization, regional comparisons, and demographic analysis."),
      
      layout_column_wrap(
        width = 1/2,
        card(
          card_header("📈 Trend Analysis"),
          plotlyOutput("trend_plot", height = "400px")
        ),
        card(
          card_header("🎯 Recent Performance"),
          plotlyOutput("recent_performance", height = "400px")
        )
      ),
      
      card(
        card_header("📋 Data Summary"),
        DTOutput("summary_table")
      )
    )
  ),
  
  # Regional Analysis Tab
  nav_panel(
    title = "🗺️ Regional Analysis",
    layout_column_wrap(
      width = 1/2,
      card(
        card_header("Regional Case Rates (per 100K population)"),
        plotlyOutput("regional_cases_plot", height = "400px")
      ),
      card(
        card_header("Vaccination vs Hospital Capacity"),
        plotlyOutput("vax_capacity_plot", height = "400px")
      )
    ),
    card(
      card_header("Regional Comparison Table"),
      DTOutput("regional_table")
    )
  ),
  
  # Demographics Tab
  nav_panel(
    title = "👥 Demographics",
    layout_sidebar(
      sidebar = sidebar(
        title = "Display Options",
        width = 250,
        radioButtons(
          "demo_metric",
          "Select Metric:",
          choices = c("Cases" = "cases", 
                     "Deaths" = "deaths", 
                     "Vaccination Rate" = "vaccinated"),
          selected = "cases"
        ),
        checkboxInput(
          "show_percentages",
          "Show as percentages",
          value = FALSE
        )
      ),
      
      layout_column_wrap(
        width = 1/2,
        card(
          card_header("Age Group Distribution"),
          plotlyOutput("age_distribution", height = "400px")
        ),
        card(
          card_header("Age Group Comparison"),
          plotlyOutput("age_comparison", height = "400px")
        )
      ),
      
      card(
        card_header("Demographic Summary"),
        DTOutput("demo_table")
      )
    )
  ),
  
  # Forecasting Tab
  nav_panel(
    title = "📈 Forecasting",
    layout_sidebar(
      sidebar = sidebar(
        title = "Forecast Parameters",
        width = 280,
        sliderInput(
          "forecast_days",
          "Forecast Period (days):",
          min = 7,
          max = 90,
          value = 30,
          step = 7
        ),
        selectInput(
          "forecast_metric",
          "Forecast Metric:",
          choices = c("Cases" = "cases", 
                     "Deaths" = "deaths", 
                     "Hospitalizations" = "hospitalizations"),
          selected = "cases"
        ),
        sliderInput(
          "confidence_level",
          "Confidence Level:",
          min = 80,
          max = 99,
          value = 95,
          step = 5,
          post = "%"
        ),
        br(),
        h4("Model Information"),
        p("Simple trend-based forecast for demonstration purposes. 
          Production models would use more sophisticated methods.")
      ),
      
      card(
        card_header("📊 Forecast Visualization"),
        plotlyOutput("forecast_plot", height = "500px")
      ),
      
      layout_column_wrap(
        width = 1/2,
        card(
          card_header("🎯 Forecast Summary"),
          uiOutput("forecast_summary")
        ),
        card(
          card_header("⚠️ Model Assumptions"),
          tags$ul(
            tags$li("Linear trend continuation"),
            tags$li("Historical variance patterns"),
            tags$li("No external intervention effects"),
            tags$li("Seasonal patterns maintained")
          )
        )
      )
    )
  )
)

# Define server logic
server <- function(input, output, session) {
  
  # Reactive data filtering
  filtered_data <- reactive({
    sample_data$time_series %>%
      filter(date >= input$date_range[1] & date <= input$date_range[2])
  })
  
  # Key statistics for sidebar
  output$key_stats <- renderUI({
    data <- filtered_data()
    metric <- input$metric
    
    total <- if (metric == "positivity_rate") {
      round(mean(data[[metric]], na.rm = TRUE), 1)
    } else {
      comma(sum(data[[metric]], na.rm = TRUE))
    }
    
    recent <- round(mean(tail(data[[metric]], 7), na.rm = TRUE), 1)
    trend_dir <- if (recent > mean(head(data[[metric]], 7), na.rm = TRUE)) "↗️" else "↘️"
    
    div(
      p(paste("Total:", total)),
      p(paste("7-day avg:", recent, trend_dir)),
      p(paste("Days:", nrow(data)))
    )
  })
  
  # Trend plot
  output$trend_plot <- renderPlotly({
    data <- filtered_data()
    metric <- input$metric
    
    # Calculate 7-day rolling average
    data$rolling_avg <- zoo::rollmean(data[[metric]], k = 7, fill = NA, align = "center")
    
    p <- plot_ly(data, x = ~date) %>%
      add_lines(y = ~get(metric), name = str_to_title(gsub("_", " ", metric)), 
                line = list(color = 'steelblue', width = 2), alpha = 0.6) %>%
      add_lines(y = ~rolling_avg, name = '7-day Average', 
                line = list(color = 'red', width = 3), alpha = 0.8) %>%
      layout(
        title = paste(str_to_title(gsub("_", " ", metric)), "Over Time"),
        xaxis = list(title = "Date"),
        yaxis = list(title = str_to_title(gsub("_", " ", metric))),
        hovermode = 'x unified'
      )
    
    p
  })
  
  # Recent performance plot
  output$recent_performance <- renderPlotly({
    data <- tail(filtered_data(), 30)  # Last 30 days
    
    metrics_data <- data.frame(
      metric = c("Cases", "Deaths", "Hospitalizations"),
      value = c(
        mean(data$cases, na.rm = TRUE),
        mean(data$deaths, na.rm = TRUE),
        mean(data$hospitalizations, na.rm = TRUE)
      )
    )
    
    colors <- brewer.pal(3, "Set2")
    
    p <- plot_ly(metrics_data, x = ~metric, y = ~value, type = 'bar',
                 marker = list(color = colors), text = ~round(value, 1),
                 textposition = 'outside') %>%
      layout(
        title = "30-Day Average Metrics",
        xaxis = list(title = "Metric"),
        yaxis = list(title = "Average Daily Count"),
        showlegend = FALSE
      )
    
    p
  })
  
  # Summary table
  output$summary_table <- renderDT({
    data <- filtered_data()
    
    summary_df <- data.frame(
      Metric = c("Cases", "Deaths", "Hospitalizations", "Positivity Rate"),
      `Total/Average` = c(
        comma(sum(data$cases, na.rm = TRUE)),
        comma(sum(data$deaths, na.rm = TRUE)),
        comma(sum(data$hospitalizations, na.rm = TRUE)),
        paste0(round(mean(data$positivity_rate, na.rm = TRUE), 1), "%")
      ),
      `Daily Average` = c(
        round(mean(data$cases, na.rm = TRUE), 1),
        round(mean(data$deaths, na.rm = TRUE), 1),
        round(mean(data$hospitalizations, na.rm = TRUE), 1),
        paste0(round(mean(data$positivity_rate, na.rm = TRUE), 1), "%")
      ),
      `Peak Value` = c(
        comma(max(data$cases, na.rm = TRUE)),
        comma(max(data$deaths, na.rm = TRUE)),
        comma(max(data$hospitalizations, na.rm = TRUE)),
        paste0(round(max(data$positivity_rate, na.rm = TRUE), 1), "%")
      ),
      check.names = FALSE
    )
    
    datatable(summary_df, options = list(dom = 't', pageLength = 10))
  })
  
  # Regional cases plot
  output$regional_cases_plot <- renderPlotly({
    colors <- brewer.pal(n = nrow(sample_data$regional), "Set3")
    
    p <- plot_ly(sample_data$regional, x = ~region, y = ~case_rate, type = 'bar',
                 marker = list(color = colors), text = ~round(case_rate, 1),
                 textposition = 'outside') %>%
      layout(
        title = "Case Rates by Region (per 100K population)",
        xaxis = list(title = "Region"),
        yaxis = list(title = "Cases per 100K"),
        showlegend = FALSE
      )
    
    p
  })
  
  # Vaccination vs capacity plot
  output$vax_capacity_plot <- renderPlotly({
    p <- plot_ly(sample_data$regional, 
                 x = ~vaccination_rate, 
                 y = ~hospital_capacity,
                 size = ~total_cases,
                 color = ~case_rate,
                 colors = viridis::viridis(10),
                 text = ~paste("Region:", region,
                              "<br>Vaccination Rate:", round(vaccination_rate, 1), "%",
                              "<br>Hospital Capacity:", round(hospital_capacity, 1), "%",
                              "<br>Total Cases:", comma(total_cases),
                              "<br>Case Rate:", round(case_rate, 1)),
                 hovertemplate = "%{text}<extra></extra>",
                 type = 'scatter',
                 mode = 'markers') %>%
      layout(
        title = "Vaccination Rate vs Hospital Capacity<br><sub>Size = Total Cases, Color = Case Rate</sub>",
        xaxis = list(title = "Vaccination Rate (%)"),
        yaxis = list(title = "Hospital Capacity (%)"),
        colorbar = list(title = "Case Rate")
      )
    
    p
  })
  
  # Regional table
  output$regional_table <- renderDT({
    display_data <- sample_data$regional %>%
      mutate(
        vaccination_rate = round(vaccination_rate, 1),
        hospital_capacity = round(hospital_capacity, 1),
        population = comma(population),
        total_cases = comma(total_cases)
      )
    
    datatable(display_data, options = list(pageLength = 10, scrollX = TRUE))
  })
  
  # Age distribution plot
  output$age_distribution <- renderPlotly({
    metric <- input$demo_metric
    show_pct <- input$show_percentages
    
    data <- sample_data$age
    values <- data[[metric]]
    
    if (show_pct && metric != "vaccinated") {
      values <- values / sum(values) * 100
      ylabel <- paste(str_to_title(metric), "(%)")
    } else {
      ylabel <- str_to_title(metric)
      if (metric == "vaccinated") ylabel <- paste(ylabel, "(%)")
    }
    
    colors <- viridis::plasma(n = nrow(data))
    
    p <- plot_ly(x = ~data$age_group, y = ~values, type = 'bar',
                 marker = list(color = colors),
                 text = ~ifelse(show_pct || metric == "vaccinated", 
                               paste0(round(values, 1), "%"), 
                               round(values, 1)),
                 textposition = 'outside') %>%
      layout(
        title = paste(str_to_title(gsub("_", " ", metric)), "by Age Group"),
        xaxis = list(title = "Age Group"),
        yaxis = list(title = ylabel),
        showlegend = FALSE
      )
    
    p
  })
  
  # Age comparison radar plot
  output$age_comparison <- renderPlotly({
    # Normalize metrics for comparison
    norm_data <- sample_data$age %>%
      mutate(
        cases_norm = (cases - min(cases)) / (max(cases) - min(cases)),
        deaths_norm = (deaths - min(deaths)) / (max(deaths) - min(deaths)),
        vaccinated_norm = (vaccinated - min(vaccinated)) / (max(vaccinated) - min(vaccinated))
      )
    
    # Create radar chart using scatterpolar
    p <- plot_ly(
      type = 'scatterpolar',
      mode = 'lines+markers',
      fill = 'toself'
    ) %>%
      add_trace(
        r = c(norm_data$cases_norm, norm_data$cases_norm[1]),  # Close the plot
        theta = c(as.character(norm_data$age_group), as.character(norm_data$age_group[1])),
        name = 'Cases',
        line = list(color = 'blue'),
        fillcolor = 'rgba(0,0,255,0.1)'
      ) %>%
      add_trace(
        r = c(norm_data$deaths_norm, norm_data$deaths_norm[1]),
        theta = c(as.character(norm_data$age_group), as.character(norm_data$age_group[1])),
        name = 'Deaths',
        line = list(color = 'red'),
        fillcolor = 'rgba(255,0,0,0.1)'
      ) %>%
      add_trace(
        r = c(norm_data$vaccinated_norm, norm_data$vaccinated_norm[1]),
        theta = c(as.character(norm_data$age_group), as.character(norm_data$age_group[1])),
        name = 'Vaccinated',
        line = list(color = 'green'),
        fillcolor = 'rgba(0,255,0,0.1)'
      ) %>%
      layout(
        polar = list(
          radialaxis = list(
            visible = TRUE,
            range = c(0, 1)
          )
        ),
        title = "Age Group Comparison<br><sub>Normalized Values</sub>",
        legend = list(orientation = "h", x = 0.5, xanchor = 'center')
      )
    
    p
  })
  
  # Demographics table
  output$demo_table <- renderDT({
    display_data <- sample_data$age %>%
      mutate(
        vaccinated = round(vaccinated, 1),
        case_fatality_rate = round(deaths / cases * 100, 2)
      )
    
    datatable(display_data, options = list(pageLength = 10, scrollX = TRUE))
  })
  
  # Forecast plot
  output$forecast_plot <- renderPlotly({
    metric <- input$forecast_metric
    forecast_days <- input$forecast_days
    confidence <- input$confidence_level
    
    # Use recent data for forecast
    recent_data <- tail(sample_data$time_series, 90)
    
    # Simple linear trend forecast (for demonstration)
    x <- seq_len(nrow(recent_data))
    y <- recent_data[[metric]]
    
    # Fit linear trend
    lm_model <- lm(y ~ x)
    
    # Generate forecast
    forecast_x <- seq(length(x) + 1, length(x) + forecast_days)
    forecast_y <- predict(lm_model, newdata = data.frame(x = forecast_x))
    
    # Add uncertainty (simple approach)
    residuals_val <- residuals(lm_model)
    std_error <- sd(residuals_val)
    z_score <- case_when(
      confidence == 95 ~ 1.96,
      confidence == 99 ~ 2.58,
      TRUE ~ 1.64
    )
    
    upper_bound <- forecast_y + z_score * std_error
    lower_bound <- pmax(0, forecast_y - z_score * std_error)
    
    # Create forecast dates
    last_date <- max(recent_data$date)
    forecast_dates <- seq(last_date + days(1), by = "day", length.out = forecast_days)
    
    # Create the plot
    p <- plot_ly() %>%
      # Historical data
      add_lines(x = recent_data$date, y = recent_data[[metric]], 
                name = "Historical", 
                line = list(color = 'blue', width = 2)) %>%
      # Forecast line
      add_lines(x = forecast_dates, y = forecast_y, 
                name = "Forecast", 
                line = list(color = 'red', width = 2, dash = 'dash')) %>%
      # Confidence interval
      add_ribbons(x = forecast_dates, 
                  ymin = lower_bound, 
                  ymax = upper_bound,
                  name = paste0(confidence, "% Confidence Interval"),
                  fillcolor = 'rgba(255,0,0,0.3)', 
                  line = list(color = 'transparent')) %>%
      # Forecast start line
      add_vline(x = last_date, 
                line = list(color = 'gray', dash = 'dot', width = 1),
                annotation = list(text = "Forecast Start", showarrow = FALSE, y = 1)) %>%
      layout(
        title = paste(str_to_title(gsub("_", " ", metric)), "Forecast (", forecast_days, "days)"),
        xaxis = list(title = "Date"),
        yaxis = list(title = str_to_title(gsub("_", " ", metric))),
        hovermode = 'x unified'
      )
    
    p
  })
  
  # Forecast summary
  output$forecast_summary <- renderUI({
    metric <- input$forecast_metric
    forecast_days <- input$forecast_days
    
    # Simple calculations for demo
    recent_avg <- mean(tail(sample_data$time_series[[metric]], 7), na.rm = TRUE)
    
    # Mock forecast statistics
    forecast_avg <- recent_avg * 1.05  # Slight increase
    total_forecast <- forecast_avg * forecast_days
    peak_day <- sample(7:forecast_days, 1)
    
    div(
      h4("Forecast Highlights"),
      p(paste("📊 Average daily:", round(forecast_avg, 1))),
      p(paste("📈 Total period:", comma(round(total_forecast)))),
      p(paste("🎯 Peak expected: Day", peak_day)),
      p(paste("📅 Forecast period:", forecast_days, "days")),
      br(),
      p("⚠️ This is a demonstration forecast. Production models would incorporate 
        epidemiological parameters, interventions, and more sophisticated methods.",
        style = "font-size: 0.9em; color: #666;")
    )
  })
}

# Create the Shiny app
shinyApp(ui = ui, server = server)
