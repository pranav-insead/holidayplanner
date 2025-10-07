// Warm destinations in India with their airport codes
const warmDestinations = [
    {
        name: "Goa",
        state: "Goa",
        airport: "GOI",
        climate: "Warm & Sunny",
        avgTemp: "28°C"
    },
    {
        name: "Kochi",
        state: "Kerala",
        airport: "COK",
        climate: "Tropical",
        avgTemp: "30°C"
    },
    {
        name: "Thiruvananthapuram",
        state: "Kerala",
        airport: "TRV",
        climate: "Tropical",
        avgTemp: "29°C"
    },
    {
        name: "Mangalore",
        state: "Karnataka",
        airport: "IXE",
        climate: "Coastal",
        avgTemp: "29°C"
    },
    {
        name: "Mumbai",
        state: "Maharashtra",
        airport: "BOM",
        climate: "Warm",
        avgTemp: "27°C"
    },
    {
        name: "Jaipur",
        state: "Rajasthan",
        airport: "JAI",
        climate: "Dry & Warm",
        avgTemp: "20°C"
    },
    {
        name: "Udaipur",
        state: "Rajasthan",
        airport: "UDR",
        climate: "Pleasant",
        avgTemp: "22°C"
    }
];

// 5-star hotels and resorts data
const hotels = {
    "GOI": [
        { name: "Taj Exotica Resort & Spa", stars: 5, type: "Resort", pricePerNight: 18500 },
        { name: "The Leela Goa", stars: 5, type: "Resort", pricePerNight: 22000 },
        { name: "ITC Grand Goa", stars: 5, type: "Resort", pricePerNight: 16500 }
    ],
    "COK": [
        { name: "Grand Hyatt Kochi Bolgatty", stars: 5, type: "Hotel", pricePerNight: 12000 },
        { name: "Taj Malabar Resort & Spa", stars: 5, type: "Resort", pricePerNight: 15000 },
        { name: "Crowne Plaza Kochi", stars: 5, type: "Hotel", pricePerNight: 10500 }
    ],
    "TRV": [
        { name: "Taj Green Cove Resort & Spa", stars: 5, type: "Resort", pricePerNight: 14000 },
        { name: "Vivanta Trivandrum", stars: 5, type: "Hotel", pricePerNight: 11000 },
        { name: "Hilton Trivandrum", stars: 5, type: "Hotel", pricePerNight: 9500 }
    ],
    "IXE": [
        { name: "Vivanta Mangalore", stars: 5, type: "Hotel", pricePerNight: 8500 },
        { name: "The Gateway Hotel", stars: 5, type: "Hotel", pricePerNight: 7500 }
    ],
    "BOM": [
        { name: "Taj Mahal Palace", stars: 5, type: "Hotel", pricePerNight: 25000 },
        { name: "The Oberoi Mumbai", stars: 5, type: "Hotel", pricePerNight: 28000 },
        { name: "ITC Maratha", stars: 5, type: "Hotel", pricePerNight: 15000 }
    ],
    "JAI": [
        { name: "Taj Rambagh Palace", stars: 5, type: "Resort", pricePerNight: 20000 },
        { name: "The Oberoi Rajvilas", stars: 5, type: "Resort", pricePerNight: 35000 },
        { name: "ITC Rajputana", stars: 5, type: "Hotel", pricePerNight: 12000 }
    ],
    "UDR": [
        { name: "The Oberoi Udaivilas", stars: 5, type: "Resort", pricePerNight: 45000 },
        { name: "Taj Lake Palace", stars: 5, type: "Resort", pricePerNight: 40000 },
        { name: "The Leela Palace Udaipur", stars: 5, type: "Resort", pricePerNight: 35000 }
    ]
};

// Airlines operating direct flights
const airlines = ["Air India", "IndiGo", "Vistara", "SpiceJet", "Go First"];

// Function to check if direct flight exists
function hasDirectFlight(from, to) {
    // Major routes with direct flights
    const directRoutes = {
        "DEL": ["GOI", "COK", "TRV", "IXE", "BOM", "JAI", "UDR"],
        "IXC": ["GOI", "BOM", "JAI"]
    };
    return directRoutes[from]?.includes(to) || false;
}

// Generate flight price based on route and date
function generateFlightPrice(from, to, isDecember) {
    const basePrice = {
        "DEL-GOI": 6500, "DEL-COK": 7500, "DEL-TRV": 7800, "DEL-IXE": 7200,
        "DEL-BOM": 5500, "DEL-JAI": 4500, "DEL-UDR": 5500,
        "IXC-GOI": 8500, "IXC-BOM": 7500, "IXC-JAI": 5500
    };
    
    const route = `${from}-${to}`;
    let price = basePrice[route] || 8000;
    
    // December holidays are peak season, increase prices
    if (isDecember) {
        price *= 1.3;
    } else {
        price *= 1.15; // January is still high season
    }
    
    // Add some randomness
    price += Math.floor(Math.random() * 1000) - 500;
    
    return Math.round(price);
}

// Generate flight timing
function generateFlightTiming() {
    const departureTimes = ["06:00", "09:30", "13:15", "16:45", "20:00"];
    const durations = ["2h 15m", "2h 30m", "2h 45m", "3h 00m"];
    
    const departureTime = departureTimes[Math.floor(Math.random() * departureTimes.length)];
    const duration = durations[Math.floor(Math.random() * durations.length)];
    
    return { departureTime, duration };
}

// Main search function
async function searchPackages(departure, dateRange, tripDuration) {
    const isDecember = dateRange === "dec20-25";
    const duration = parseInt(tripDuration);
    const packages = [];
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Filter destinations with direct flights
    const availableDestinations = warmDestinations.filter(dest => 
        hasDirectFlight(departure, dest.airport)
    );
    
    // Create packages for each destination
    for (const dest of availableDestinations) {
        // Select a random hotel
        const destinationHotels = hotels[dest.airport];
        if (!destinationHotels || destinationHotels.length === 0) continue;
        
        const hotel = destinationHotels[Math.floor(Math.random() * destinationHotels.length)];
        
        // Generate flight details
        const airline = airlines[Math.floor(Math.random() * airlines.length)];
        const flightPrice = generateFlightPrice(departure, dest.airport, isDecember);
        const flightTiming = generateFlightTiming();
        
        // Calculate hotel price with some variation for season
        const hotelPricePerNight = Math.round(hotel.pricePerNight * (isDecember ? 1.2 : 1.1));
        const totalHotelPrice = hotelPricePerNight * (duration - 1); // duration - 1 nights
        
        // Calculate total package price
        const totalPrice = (flightPrice * 2) + totalHotelPrice; // Round trip flights
        
        packages.push({
            destination: dest,
            flight: {
                airline,
                price: flightPrice,
                departureTime: flightTiming.departureTime,
                duration: flightTiming.duration,
                isDirect: true
            },
            hotel: {
                name: hotel.name,
                stars: hotel.stars,
                type: hotel.type,
                pricePerNight: hotelPricePerNight,
                nights: duration - 1
            },
            totalPrice,
            tripDuration: duration
        });
    }
    
    // Sort by price
    packages.sort((a, b) => a.totalPrice - b.totalPrice);
    
    return packages;
}

// Format currency in INR
function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(price);
}

// Create package card HTML
function createPackageCard(pkg) {
    const stars = '⭐'.repeat(pkg.hotel.stars);
    
    return `
        <div class="package-card">
            <div class="package-header">
                <div class="destination-name">${pkg.destination.name}</div>
                <div class="destination-state">${pkg.destination.state} • ${pkg.destination.climate}</div>
            </div>
            <div class="package-body">
                <div class="flight-section">
                    <div class="section-title">Flight Details</div>
                    <div class="flight-info">
                        <div class="info-row">
                            <span class="info-label">Airline:</span>
                            <span class="info-value">${pkg.flight.airline}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Departure:</span>
                            <span class="info-value">${pkg.flight.departureTime}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Duration:</span>
                            <span class="info-value">${pkg.flight.duration}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Type:</span>
                            <span class="direct-badge">DIRECT</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Flight Price:</span>
                            <span class="info-value">${formatPrice(pkg.flight.price)} × 2</span>
                        </div>
                    </div>
                </div>
                
                <div class="hotel-section">
                    <div class="section-title">Hotel Details</div>
                    <div class="hotel-info">
                        <div class="info-row">
                            <span class="info-label">Hotel:</span>
                            <span class="info-value">${pkg.hotel.name}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Rating:</span>
                            <span class="star-rating">${stars}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Type:</span>
                            <span class="info-value">${pkg.hotel.type}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Nights:</span>
                            <span class="info-value">${pkg.hotel.nights}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Per Night:</span>
                            <span class="info-value">${formatPrice(pkg.hotel.pricePerNight)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="price-section">
                    <div class="price-label">Total Package Price</div>
                    <div class="price-value">${formatPrice(pkg.totalPrice)}</div>
                    <div class="price-per-person">Per person (${pkg.tripDuration} days)</div>
                </div>
                
                <button class="book-btn" onclick="bookPackage('${pkg.destination.name}')">
                    Book Now
                </button>
            </div>
        </div>
    `;
}

// Book package function
function bookPackage(destinationName) {
    alert(`Booking functionality would redirect to payment gateway for ${destinationName} package.\n\nThis is a demo. In production, this would integrate with:\n- Flight booking APIs (Amadeus, Skyscanner)\n- Hotel booking APIs (Booking.com, Hotels.com)\n- Payment gateway (Razorpay, PayTM)`);
}

// Handle form submission
document.getElementById('searchForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const departure = document.getElementById('departure').value;
    const dateRange = document.getElementById('dateRange').value;
    const tripDuration = document.getElementById('tripDuration').value;
    
    if (!departure || !dateRange || !tripDuration) {
        alert('Please fill in all fields');
        return;
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('noResults').style.display = 'none';
    
    try {
        // Search for packages
        const packages = await searchPackages(departure, dateRange, tripDuration);
        
        // Hide loading
        document.getElementById('loading').style.display = 'none';
        
        if (packages.length === 0) {
            document.getElementById('noResults').style.display = 'block';
        } else {
            // Display results
            const packagesList = document.getElementById('packagesList');
            packagesList.innerHTML = packages.map(pkg => createPackageCard(pkg)).join('');
            document.getElementById('results').style.display = 'block';
            
            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Error searching packages:', error);
        document.getElementById('loading').style.display = 'none';
        alert('An error occurred while searching. Please try again.');
    }
});

// Initialize with default values for quick demo
window.addEventListener('DOMContentLoaded', function() {
    console.log('Holiday Planner initialized');
    console.log('API Integration Notes:');
    console.log('- For live flight prices: Use Amadeus API or Skyscanner API');
    console.log('- For live hotel prices: Use Booking.com API or Hotels.com API');
    console.log('- Current version uses realistic sample data for demonstration');
});
