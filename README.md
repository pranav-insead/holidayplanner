# 🌴 Holiday Planner - Dec-Jan Warm Destinations

A web application for planning holiday trips to warm destinations in India during December-January. Find 2-3 day trips from Chandigarh or Delhi with live prices for 5-star hotels/resorts and direct flights.

## Features

✈️ **Flight Search**
- Direct flights only from Chandigarh (IXC) or Delhi (DEL)
- Multiple airlines (Air India, IndiGo, Vistara, SpiceJet, Go First)
- Live pricing with seasonal variations
- Round-trip bookings

🏨 **Hotel Search**
- 5-star hotels and resorts only
- Premium properties (Taj, Oberoi, Leela, ITC, Vivanta, etc.)
- Per-night pricing for 2-3 day trips

🌞 **Warm Destinations**
- Goa (Beach paradise)
- Kerala (Kochi, Thiruvananthapuram)
- Karnataka (Mangalore)
- Maharashtra (Mumbai)
- Rajasthan (Jaipur, Udaipur)

📅 **Travel Dates**
- December 20-25, 2024
- January 02-08, 2025

## Quick Start

1. Open `index.html` in a web browser
2. Select your departure city (Delhi or Chandigarh)
3. Choose travel dates (Dec 20-25 or Jan 02-08)
4. Select trip duration (2 or 3 days)
5. Click "Search Packages" to view available options

## File Structure

```
holidayplanner/
├── index.html      # Main HTML page with search form
├── styles.css      # Styling and responsive design
├── app.js          # JavaScript logic for search and display
└── README.md       # Documentation
```

## How It Works

The application provides:
1. **Search Form**: User selects departure city, dates, and duration
2. **Package Search**: Filters destinations with direct flights
3. **Price Calculation**: 
   - Flight prices (round trip)
   - Hotel prices (per night × nights)
   - Total package price
4. **Results Display**: Cards showing flight details, hotel info, and pricing

## API Integration (For Production)

This demo uses realistic sample data. For live prices, integrate these APIs:

### Flight APIs
- **Amadeus API** (Recommended)
  - Endpoint: `GET /v2/shopping/flight-offers`
  - Supports direct flight filtering
  - Real-time pricing
  
- **Skyscanner API**
  - Flight search with carrier filtering
  - Price monitoring

### Hotel APIs
- **Booking.com API**
  - Filter by star rating (5 stars)
  - Property types (hotels, resorts)
  - Real-time availability and pricing

- **Hotels.com API**
  - Premium property search
  - Detailed amenities and reviews

### Implementation Steps
1. Register for API keys from providers
2. Replace sample data in `app.js` with API calls
3. Add error handling and rate limiting
4. Implement caching for better performance

## Sample API Integration Code

```javascript
// Example: Amadeus Flight Search
async function searchFlights(origin, destination, departureDate) {
    const response = await fetch('https://api.amadeus.com/v2/shopping/flight-offers', {
        headers: {
            'Authorization': `Bearer ${API_TOKEN}`
        },
        params: {
            originLocationCode: origin,
            destinationLocationCode: destination,
            departureDate: departureDate,
            adults: 1,
            nonStop: true  // Direct flights only
        }
    });
    return await response.json();
}

// Example: Booking.com Hotel Search
async function searchHotels(destination, checkIn, checkOut) {
    const response = await fetch('https://api.booking.com/v1/hotels/search', {
        headers: {
            'Authorization': `Bearer ${API_TOKEN}`
        },
        params: {
            destination: destination,
            checkin: checkIn,
            checkout: checkOut,
            stars: 5  // 5-star only
        }
    });
    return await response.json();
}
```

## Technologies Used

- **HTML5**: Structure and semantic markup
- **CSS3**: Styling with gradients and responsive design
- **JavaScript (ES6+)**: Dynamic content and search logic
- **No external dependencies**: Pure vanilla JavaScript

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Future Enhancements

- [ ] Live API integration for real-time prices
- [ ] User authentication and booking history
- [ ] Payment gateway integration
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Mobile app version
- [ ] Comparison with other date ranges
- [ ] Reviews and ratings integration

## Development

To modify the application:

1. **Add new destinations**: Update `warmDestinations` array in `app.js`
2. **Add new hotels**: Update `hotels` object in `app.js`
3. **Modify pricing logic**: Edit `generateFlightPrice()` function
4. **Change styling**: Modify `styles.css`

## License

This project is open source and available for use.

## Support

For issues or questions, please open an issue on the repository.
