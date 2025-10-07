// API Integration Example
// This file demonstrates how to integrate real travel APIs for live pricing

/**
 * AMADEUS API Integration for Flights
 * Documentation: https://developers.amadeus.com/
 */

// 1. Get Amadeus API Token
async function getAmadeusToken() {
    const response = await fetch('https://api.amadeus.com/v1/security/oauth2/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'grant_type': 'client_credentials',
            'client_id': 'YOUR_API_KEY',
            'client_secret': 'YOUR_API_SECRET'
        })
    });
    const data = await response.json();
    return data.access_token;
}

// 2. Search for Direct Flights
async function searchAmadeusFlights(token, origin, destination, departureDate) {
    const response = await fetch(
        `https://api.amadeus.com/v2/shopping/flight-offers?` + 
        new URLSearchParams({
            originLocationCode: origin,
            destinationLocationCode: destination,
            departureDate: departureDate,
            adults: '1',
            nonStop: 'true',  // Direct flights only
            currencyCode: 'INR',
            max: '10'
        }), {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return await response.json();
}

/**
 * BOOKING.COM API Integration for Hotels
 * Documentation: https://developers.booking.com/
 */

async function searchBookingHotels(destination, checkIn, checkOut) {
    const response = await fetch(
        `https://api.booking.com/v1/hotels/search?` +
        new URLSearchParams({
            city: destination,
            checkin: checkIn,
            checkout: checkOut,
            room_number: '1',
            adults_number: '1',
            min_rating: '5',  // 5-star only
            currency: 'INR'
        }), {
        headers: {
            'Authorization': 'Bearer YOUR_API_KEY'
        }
    });
    return await response.json();
}

/**
 * HOTELS.COM API Integration Alternative
 */

async function searchHotelsComProperties(latitude, longitude, checkIn, checkOut) {
    const response = await fetch(
        'https://hotels-com-provider.p.rapidapi.com/v1/hotels/search', {
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            'X-RapidAPI-Key': 'YOUR_RAPIDAPI_KEY',
            'X-RapidAPI-Host': 'hotels-com-provider.p.rapidapi.com'
        },
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude,
            checkin: checkIn,
            checkout: checkOut,
            adults: 1,
            star_rating: [5]  // 5-star only
        })
    });
    return await response.json();
}

/**
 * SKYSCANNER API Integration Alternative
 */

async function searchSkyscannerFlights(origin, destination, outboundDate) {
    const response = await fetch(
        `https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browseroutes/v1.0/IN/INR/en-IN/${origin}/${destination}/${outboundDate}`, {
        headers: {
            'X-RapidAPI-Key': 'YOUR_RAPIDAPI_KEY',
            'X-RapidAPI-Host': 'skyscanner-skyscanner-flight-search-v1.p.rapidapi.com'
        }
    });
    return await response.json();
}

/**
 * Integration into the main app.js
 * Replace the searchPackages function with this implementation
 */

async function searchPackagesWithLiveAPIs(departure, dateRange, tripDuration) {
    const isDecember = dateRange === "dec20-25";
    const duration = parseInt(tripDuration);
    
    // Calculate dates
    const departureDate = isDecember ? "2024-12-20" : "2025-01-02";
    const returnDate = isDecember 
        ? `2024-12-${20 + duration - 1}` 
        : `2025-01-${2 + duration - 1}`;
    
    const packages = [];
    
    // Get API token
    const token = await getAmadeusToken();
    
    // Search for each destination
    for (const dest of warmDestinations) {
        try {
            // 1. Search flights
            const flightData = await searchAmadeusFlights(
                token, 
                departure, 
                dest.airport, 
                departureDate
            );
            
            if (!flightData.data || flightData.data.length === 0) continue;
            
            const flight = flightData.data[0];
            const flightPrice = parseFloat(flight.price.total);
            
            // 2. Search hotels
            const hotelData = await searchBookingHotels(
                dest.name,
                departureDate,
                returnDate
            );
            
            if (!hotelData.result || hotelData.result.length === 0) continue;
            
            const hotel = hotelData.result[0];
            const hotelTotalPrice = parseFloat(hotel.price.total);
            const hotelPricePerNight = hotelTotalPrice / (duration - 1);
            
            // 3. Create package
            packages.push({
                destination: dest,
                flight: {
                    airline: flight.validatingAirlineCodes[0],
                    price: flightPrice,
                    departureTime: flight.itineraries[0].segments[0].departure.at,
                    duration: flight.itineraries[0].duration,
                    isDirect: true
                },
                hotel: {
                    name: hotel.hotel_name,
                    stars: 5,
                    type: hotel.property_type,
                    pricePerNight: Math.round(hotelPricePerNight),
                    nights: duration - 1
                },
                totalPrice: (flightPrice * 2) + hotelTotalPrice,
                tripDuration: duration
            });
        } catch (error) {
            console.error(`Error fetching data for ${dest.name}:`, error);
            continue;
        }
    }
    
    // Sort by price
    packages.sort((a, b) => a.totalPrice - b.totalPrice);
    
    return packages;
}

/**
 * Environment Variables Setup
 * 
 * For security, store API keys in environment variables or a config file:
 * 
 * 1. Create a .env file:
 *    AMADEUS_API_KEY=your_key_here
 *    AMADEUS_API_SECRET=your_secret_here
 *    BOOKING_API_KEY=your_key_here
 *    RAPIDAPI_KEY=your_key_here
 * 
 * 2. Add .env to .gitignore
 * 
 * 3. Use a library like dotenv to load variables
 */

/**
 * Rate Limiting and Caching
 * 
 * To avoid hitting API rate limits:
 * 1. Implement request caching (cache results for 5-10 minutes)
 * 2. Use debouncing on search requests
 * 3. Consider using a backend proxy server
 */

// Example cache implementation
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

async function cachedSearch(key, searchFunction) {
    const cached = cache.get(key);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        return cached.data;
    }
    
    const data = await searchFunction();
    cache.set(key, { data, timestamp: Date.now() });
    return data;
}

/**
 * Error Handling
 */

function handleAPIError(error, provider) {
    console.error(`Error from ${provider}:`, error);
    
    if (error.status === 429) {
        alert('Too many requests. Please try again in a few minutes.');
    } else if (error.status === 401) {
        alert('Authentication failed. Please check your API keys.');
    } else {
        alert(`An error occurred while fetching data from ${provider}.`);
    }
}

/**
 * Cost Estimation
 * 
 * API costs (approximate):
 * - Amadeus: Free tier includes 2,000 requests/month
 * - Booking.com: Varies by partner agreement
 * - RapidAPI (Skyscanner, Hotels.com): ~$0.01-0.10 per request
 * 
 * For production, consider:
 * - Backend caching layer
 * - Request batching
 * - User authentication to prevent abuse
 */
