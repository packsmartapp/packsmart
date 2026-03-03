export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') return res.status(200).end();

    const API_KEY = process.env.OPENWEATHER_API_KEY;
    if (!API_KEY) {
        return res.status(200).json({
            success: false,
            error: 'Weather API key not configured'
        });
    }

    const city = req.query.city;
    if (!city) {
        return res.status(400).json({ success: false, error: 'City parameter required' });
    }

    try {
        const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&units=metric&appid=${API_KEY}`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.cod !== 200) {
            return res.status(200).json({
                success: false,
                error: data.message || 'City not found'
            });
        }

        return res.status(200).json({
            success: true,
            weather: {
                temp: data.main.temp,
                feelsLike: data.main.feels_like,
                tempMin: data.main.temp_min,
                tempMax: data.main.temp_max,
                humidity: data.main.humidity,
                description: data.weather[0].description,
                icon: data.weather[0].icon,
                windSpeed: Math.round(data.wind.speed * 3.6), // m/s to km/h
                city: data.name,
                country: data.sys.country
            }
        });
    } catch (err) {
        return res.status(200).json({
            success: false,
            error: err.message || 'Weather fetch failed'
        });
    }
}
