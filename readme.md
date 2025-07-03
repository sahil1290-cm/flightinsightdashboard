# Flight Analytics Dashboard

## Overview

This is a Flask-based web application that provides flight data analytics with AI-powered insights. The system generates synthetic flight data, analyzes pricing trends, and provides intelligent recommendations using OpenAI's GPT models. The application features a modern dark-themed UI with interactive charts and comprehensive flight analysis capabilities.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **UI Framework**: Bootstrap 5 with custom dark theme
- **Visualization**: Plotly.js for interactive charts
- **Icons**: Font Awesome 6.0
- **Styling**: Custom CSS with responsive design

### Backend Architecture
- **Web Framework**: Flask (Python)
- **Data Processing**: Pandas for data manipulation
- **AI Integration**: OpenAI API for intelligent insights
- **Data Generation**: Custom flight data generator with realistic pricing models

### Key Components
- **Main Application** (`app.py`): Flask routes and request handling
- **Flight Data Generator** (`flight_data.py`): Synthetic flight data creation
- **AI Insights Generator** (`openai_insights.py`): OpenAI-powered analysis
- **Templates**: HTML templates with Bootstrap styling
- **Static Assets**: CSS and JavaScript for frontend functionality

## Data Flow

1. **User Input**: Users submit search criteria (origin, destination, date range)
2. **Data Generation**: System generates realistic flight data based on parameters
3. **Data Processing**: Pandas processes and analyzes the generated data
4. **AI Analysis**: OpenAI generates insights from flight data patterns
5. **Visualization**: Plotly creates interactive charts and graphs
6. **Dashboard Display**: Results presented in a comprehensive dashboard

## External Dependencies

### Required Python Packages
- Flask: Web framework
- Pandas: Data manipulation
- Plotly: Data visualization
- OpenAI: AI insights generation

### CDN Dependencies
- Bootstrap 5: UI framework
- Font Awesome: Icons
- Plotly.js: Chart rendering

### API Keys
- OpenAI API key (required for AI insights, falls back to static insights if unavailable)

## Deployment Strategy

- **Development**: Flask development server with debug mode
- **Production Ready**: Can be deployed to any Python hosting platform
- **Environment Variables**: 
  - `OPENAI_API_KEY`: For AI insights functionality
  - `SESSION_SECRET`: For Flask session security
- **Static Files**: Served through Flask's static file handler

## Changelog

- July 03, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.