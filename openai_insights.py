import os
import json
import logging
from openai import OpenAI

class FlightInsightsGenerator:
    """Generate AI-powered insights from flight data using OpenAI"""
    
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logging.warning("OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def generate_insights(self, flight_data):
        """Generate insights from flight data using OpenAI"""
        if not self.client:
            return self._generate_fallback_insights(flight_data)
        
        try:
            # Prepare data summary for OpenAI
            data_summary = self._prepare_data_summary(flight_data)
            
            # Generate insights using OpenAI
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a flight data analyst expert. Analyze the provided flight data and generate actionable insights about pricing trends, demand patterns, and travel recommendations. Respond with JSON in the following format: {'popular_routes': ['route1', 'route2'], 'price_insights': 'text analysis', 'demand_patterns': 'text analysis', 'recommendations': ['recommendation1', 'recommendation2'], 'key_statistics': {'avg_price': number, 'cheapest_day': 'day', 'most_expensive_day': 'day', 'total_flights': number}}"
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this flight data and provide insights: {json.dumps(data_summary, indent=2)}"
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            insights = json.loads(response.choices[0].message.content)
            logging.info("Successfully generated OpenAI insights")
            return insights
            
        except Exception as e:
            logging.error(f"Error generating OpenAI insights: {e}")
            return self._generate_fallback_insights(flight_data)
    
    def _prepare_data_summary(self, flight_data):
        """Prepare a summary of flight data for OpenAI analysis"""
        if not flight_data:
            return {}
        
        # Calculate basic statistics
        prices = [flight['price'] for flight in flight_data]
        routes = [flight['route'] for flight in flight_data]
        days = [flight['day_of_week'] for flight in flight_data]
        airlines = [flight['airline'] for flight in flight_data]
        
        # Count occurrences
        from collections import Counter
        route_counts = Counter(routes)
        day_counts = Counter(days)
        airline_counts = Counter(airlines)
        
        # Calculate price statistics by day
        price_by_day = {}
        for flight in flight_data:
            day = flight['day_of_week']
            if day not in price_by_day:
                price_by_day[day] = []
            price_by_day[day].append(flight['price'])
        
        avg_price_by_day = {
            day: sum(prices) / len(prices) 
            for day, prices in price_by_day.items()
        }
        
        return {
            'total_flights': len(flight_data),
            'price_range': {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices)
            },
            'most_popular_routes': dict(route_counts.most_common(5)),
            'flights_by_day': dict(day_counts),
            'avg_price_by_day': avg_price_by_day,
            'top_airlines': dict(airline_counts.most_common(5)),
            'date_range': {
                'start': min(flight['date'] for flight in flight_data),
                'end': max(flight['date'] for flight in flight_data)
            }
        }
    
    def _generate_fallback_insights(self, flight_data):
        """Generate basic insights when OpenAI is not available"""
        if not flight_data:
            return {
                'popular_routes': [],
                'price_insights': 'No flight data available for analysis.',
                'demand_patterns': 'Unable to analyze demand patterns without data.',
                'recommendations': ['Please try a different search criteria.'],
                'key_statistics': {
                    'avg_price': 0,
                    'cheapest_day': 'Unknown',
                    'most_expensive_day': 'Unknown',
                    'total_flights': 0
                }
            }
        
        # Calculate basic statistics
        prices = [flight['price'] for flight in flight_data]
        routes = [flight['route'] for flight in flight_data]
        
        # Group by day of week
        from collections import defaultdict
        prices_by_day = defaultdict(list)
        for flight in flight_data:
            prices_by_day[flight['day_of_week']].append(flight['price'])
        
        # Calculate averages
        avg_prices_by_day = {
            day: sum(prices) / len(prices) 
            for day, prices in prices_by_day.items()
        }
        
        # Find cheapest and most expensive days
        cheapest_day = min(avg_prices_by_day, key=avg_prices_by_day.get)
        most_expensive_day = max(avg_prices_by_day, key=avg_prices_by_day.get)
        
        # Most popular routes
        from collections import Counter
        route_counts = Counter(routes)
        popular_routes = [route for route, count in route_counts.most_common(3)]
        
        # Generate insights text
        avg_price = sum(prices) / len(prices)
        price_insights = f"Average flight price is ${avg_price:.2f}. Prices range from ${min(prices)} to ${max(prices)}. "
        price_insights += f"The cheapest flights are typically found on {cheapest_day}s (${avg_prices_by_day[cheapest_day]:.2f} avg), "
        price_insights += f"while {most_expensive_day}s tend to be most expensive (${avg_prices_by_day[most_expensive_day]:.2f} avg)."
        
        demand_patterns = f"Analysis of {len(flight_data)} flights shows varying demand patterns throughout the week. "
        demand_patterns += f"Weekend flights ({cheapest_day != 'Saturday' and cheapest_day != 'Sunday' and 'weekends' or 'weekdays'}) "
        demand_patterns += "generally show different pricing patterns compared to weekdays."
        
        recommendations = [
            f"Consider flying on {cheapest_day}s for the best prices",
            f"Avoid {most_expensive_day}s if looking for budget options",
            "Book in advance for better pricing options",
            "Compare different airlines for the same route"
        ]
        
        return {
            'popular_routes': popular_routes,
            'price_insights': price_insights,
            'demand_patterns': demand_patterns,
            'recommendations': recommendations,
            'key_statistics': {
                'avg_price': round(avg_price, 2),
                'cheapest_day': cheapest_day,
                'most_expensive_day': most_expensive_day,
                'total_flights': len(flight_data)
            }
        }
