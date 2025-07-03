import random
from datetime import datetime, timedelta
import logging

class FlightDataGenerator:
    """Generate realistic flight data for analysis"""
    
    def __init__(self):
        self.airlines = [
            'American Airlines', 'Delta Air Lines', 'United Airlines',
            'Southwest Airlines', 'JetBlue Airways', 'Alaska Airlines',
            'Spirit Airlines', 'Frontier Airlines'
        ]
        
        self.aircraft_types = [
            'Boeing 737', 'Airbus A320', 'Boeing 757', 'Airbus A321',
            'Boeing 777', 'Airbus A330', 'Boeing 787', 'Embraer E175'
        ]
        
        # Base prices for different route types
        self.base_prices = {
            'short_haul': (150, 400),    # Under 3 hours
            'medium_haul': (300, 700),   # 3-6 hours
            'long_haul': (500, 1200)     # Over 6 hours
        }
        
        # Price multipliers based on factors
        self.price_multipliers = {
            'weekend': 1.3,
            'holiday': 1.5,
            'peak_season': 1.4,
            'red_eye': 0.8,
            'early_morning': 0.9
        }
    
    def generate_flight_data(self, from_city, to_city, start_date, end_date):
        """Generate flight data for the specified route and date range"""
        try:
            flights = []
            current_date = start_date
            
            # Calculate route type based on cities (simplified logic)
            route_type = self._determine_route_type(from_city, to_city)
            
            while current_date <= end_date:
                # Generate 3-8 flights per day
                daily_flights = random.randint(3, 8)
                
                for _ in range(daily_flights):
                    flight = self._generate_single_flight(
                        from_city, to_city, current_date, route_type
                    )
                    flights.append(flight)
                
                current_date += timedelta(days=1)
            
            logging.info(f"Generated {len(flights)} flights for {from_city} to {to_city}")
            return flights
            
        except Exception as e:
            logging.error(f"Error generating flight data: {e}")
            return []
    
    def _determine_route_type(self, from_city, to_city):
        """Determine if route is short, medium, or long haul"""
        # Simplified logic - in reality, you'd use distance/time data
        major_cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
        international_indicators = ['London', 'Paris', 'Tokyo', 'Sydney', 'Dubai']
        
        if any(city in from_city + to_city for city in international_indicators):
            return 'long_haul'
        elif all(city in from_city + to_city for city in major_cities):
            return 'medium_haul'
        else:
            return 'short_haul'
    
    def _generate_single_flight(self, from_city, to_city, date, route_type):
        """Generate a single flight record"""
        # Basic flight info
        airline = random.choice(self.airlines)
        aircraft = random.choice(self.aircraft_types)
        flight_number = f"{airline[:2].upper()}{random.randint(100, 9999)}"
        
        # Generate departure time
        departure_hour = random.randint(5, 22)
        departure_minute = random.choice([0, 15, 30, 45])
        departure_time = f"{departure_hour:02d}:{departure_minute:02d}"
        
        # Generate flight duration based on route type
        if route_type == 'short_haul':
            duration_hours = random.randint(1, 3)
        elif route_type == 'medium_haul':
            duration_hours = random.randint(3, 6)
        else:  # long_haul
            duration_hours = random.randint(6, 15)
        
        duration_minutes = random.randint(0, 59)
        duration = f"{duration_hours}h {duration_minutes}m"
        
        # Calculate arrival time
        departure_dt = datetime.combine(date, datetime.strptime(departure_time, '%H:%M').time())
        arrival_dt = departure_dt + timedelta(hours=duration_hours, minutes=duration_minutes)
        arrival_time = arrival_dt.strftime('%H:%M')
        
        # Generate price with various factors
        base_price_range = self.base_prices[route_type]
        base_price = random.randint(base_price_range[0], base_price_range[1])
        
        # Apply price multipliers
        price_multiplier = 1.0
        
        # Weekend premium
        if date.weekday() >= 5:  # Saturday or Sunday
            price_multiplier *= self.price_multipliers['weekend']
        
        # Holiday premium (simplified - around major holidays)
        if date.month in [12, 1, 7]:  # Winter holidays and summer
            price_multiplier *= self.price_multipliers['holiday']
        
        # Time of day adjustments
        if departure_hour < 6:  # Red-eye flights
            price_multiplier *= self.price_multipliers['red_eye']
        elif departure_hour < 9:  # Early morning
            price_multiplier *= self.price_multipliers['early_morning']
        
        # Add some randomness
        price_multiplier *= random.uniform(0.8, 1.2)
        
        final_price = int(base_price * price_multiplier)
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'airline': airline,
            'flight_number': flight_number,
            'aircraft': aircraft,
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'duration': duration,
            'price': final_price,
            'route': f"{from_city} → {to_city}",
            'from_city': from_city,
            'to_city': to_city,
            'day_of_week': date.strftime('%A'),
            'route_type': route_type
        }
