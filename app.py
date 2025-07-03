import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json
from flight_data import FlightDataGenerator
from openai_insights import FlightInsightsGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize data generators
flight_data_generator = FlightDataGenerator()
insights_generator = FlightInsightsGenerator()

@app.route('/')
def index():
    """Main page with search form"""
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """Dashboard page with flight analysis"""
    if request.method == 'POST':
        # Get form data
        from_city = request.form.get('from_city', '').strip()
        to_city = request.form.get('to_city', '').strip()
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        
        # Validate inputs
        if not all([from_city, to_city, start_date, end_date]):
            flash('Please fill in all fields', 'error')
            return redirect(url_for('index'))
        
        try:
            # Parse dates
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_date_obj >= end_date_obj:
                flash('End date must be after start date', 'error')
                return redirect(url_for('index'))
            
            # Generate flight data
            app.logger.info(f"Generating flight data for {from_city} to {to_city}")
            flight_data = flight_data_generator.generate_flight_data(
                from_city, to_city, start_date_obj, end_date_obj
            )
            
            if not flight_data:
                flash('No flight data available for the selected criteria', 'error')
                return redirect(url_for('index'))
            
            # Generate AI insights
            app.logger.info("Generating AI insights")
            insights = insights_generator.generate_insights(flight_data)
            
            # Create visualizations
            charts = create_charts(flight_data)
            
            return render_template('dashboard.html',
                                 flight_data=flight_data,
                                 insights=insights,
                                 charts=charts,
                                 search_params={
                                     'from_city': from_city,
                                     'to_city': to_city,
                                     'start_date': start_date,
                                     'end_date': end_date
                                 })
            
        except ValueError as e:
            app.logger.error(f"Date parsing error: {e}")
            flash('Invalid date format', 'error')
            return redirect(url_for('index'))
        except Exception as e:
            app.logger.error(f"Dashboard error: {e}")
            flash('An error occurred while processing your request', 'error')
            return redirect(url_for('index'))
    
    return redirect(url_for('index'))

def create_charts(flight_data):
    """Create Plotly charts from flight data"""
    df = pd.DataFrame(flight_data)
    
    # Price trend chart
    price_trend = go.Scatter(
        x=df['date'],
        y=df['price'],
        mode='lines+markers',
        name='Price Trend',
        line=dict(color='#007bff', width=3),
        marker=dict(size=8)
    )
    
    price_chart = go.Figure(data=[price_trend])
    price_chart.update_layout(
        title='Flight Price Trend Over Time',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        template='plotly_dark',
        height=400
    )
    
    # Popular routes chart (by frequency)
    route_counts = df['route'].value_counts().head(10)
    
    routes_chart = go.Figure(data=[
        go.Bar(
            x=route_counts.index,
            y=route_counts.values,
            marker_color='#28a745'
        )
    ])
    
    routes_chart.update_layout(
        title='Most Popular Routes',
        xaxis_title='Route',
        yaxis_title='Number of Flights',
        template='plotly_dark',
        height=400,
        xaxis_tickangle=-45
    )
    
    # Demand by day of week
    df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name()
    demand_by_day = df.groupby('day_of_week')['price'].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    
    demand_chart = go.Figure(data=[
        go.Bar(
            x=demand_by_day.index,
            y=demand_by_day.values,
            marker_color='#ffc107'
        )
    ])
    
    demand_chart.update_layout(
        title='Average Price by Day of Week',
        xaxis_title='Day of Week',
        yaxis_title='Average Price ($)',
        template='plotly_dark',
        height=400
    )
    
    # Convert charts to JSON for template
    charts = {
        'price_trend': json.dumps(price_chart, cls=plotly.utils.PlotlyJSONEncoder),
        'popular_routes': json.dumps(routes_chart, cls=plotly.utils.PlotlyJSONEncoder),
        'demand_by_day': json.dumps(demand_chart, cls=plotly.utils.PlotlyJSONEncoder)
    }
    
    return charts

@app.route('/api/refresh-insights', methods=['POST'])
def refresh_insights():
    """API endpoint to refresh insights"""
    try:
        data = request.get_json()
        flight_data = data.get('flight_data', [])
        
        if not flight_data:
            return jsonify({'error': 'No flight data provided'}), 400
        
        insights = insights_generator.generate_insights(flight_data)
        return jsonify({'insights': insights})
    
    except Exception as e:
        app.logger.error(f"Insights refresh error: {e}")
        return jsonify({'error': 'Failed to refresh insights'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
