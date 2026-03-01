import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

/**
 * BELGIUM AIR PINPOINT - FRONTEND
 * Optimized for high performance and high-detail terrain.
 * Features: Hyper-local search, 200km GIS limit, XAI insights, Visual Ruler.
 * Fixed: Map tiles updated for better road/terrain/water visibility.
 */

const PROJECT_NAME = "Belgium Air Pinpoint";
const API_KEY = 'cd505863f1197b924659fb4fb195ba30'; 
const BELGIUM_BOUNDS = [
    [49.4969, 2.3847], // South-West
    [51.5517, 6.4081]  // North-East
];

// --- STABLE SVG ICONS (Professional Design, Emoji-Free) ---
const Icons = {
  Car: () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/></svg>,
  Tree: () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20v-8"/><path d="M19 12a7 7 0 1 0-14 0c0 1.5.5 2.9 1.3 4.1L5 20h14l-1.3-3.9c.8-1.2 1.3-2.6 1.3-4.1Z"/><path d="M12 12a3 3 0 0 1 0-6 3 3 0 0 1 0 6Z"/></svg>,
  Factory: () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 20V9l4-2v13"/><path d="M18 20V7l4-2v15"/><path d="M10 20V5l4-2v17"/><path d="M2 20h20"/></svg>,
  Info: () => <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>,
  Wind: () => <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2"/><path d="M9.6 4.6A2 2 0 1 1 11 8H2"/><path d="M12.6 19.4A2 2 0 1 0 14 16H2"/></svg>,
  Activity: () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>,
  ShieldCheck: ({ color }) => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>,
  MapPin: ({ opacity = 1 }) => <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" style={{ opacity }}><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>,
  Search: () => <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>,
  Navigation: () => <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
};

export default function App() {
    const [prediction, setPrediction] = useState(null);
    const [status, setStatus] = useState("Select a coordinate in Belgium to analyze PM2.5");
    const [clickCoords, setClickCoords] = useState(null);
    const [libLoaded, setLibLoaded] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [isSearching, setIsSearching] = useState(false);

    const mapRef = useRef(null);
    const mapInstance = useRef(null);
    const rulerInstance = useRef(null);

    // --- OPTIMIZED LIBRARY LOADING ---
    useEffect(() => {
        if (window.L) {
            setLibLoaded(true);
            return;
        }
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);

        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.async = true;
        script.onload = () => setLibLoaded(true);
        document.head.appendChild(script);
    }, []);

    // --- MAP INITIALIZATION ---
    useEffect(() => {
        if (!libLoaded || !mapRef.current || mapInstance.current) return;
        const L = window.L;
        const map = L.map(mapRef.current, {
            center: [50.85, 4.35],
            zoom: 10,
            minZoom: 8,
            maxZoom: 18,
            maxBounds: BELGIUM_BOUNDS,
            maxBoundsViscosity: 1.0
        });

        // Use CartoDB Voyager tiles - very crisp, shows roads, water, and green terrain clearly.
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(map);

        map.on('click', async (e) => {
            const { lat, lng } = e.latlng;
            handleInferenceRequest(lat, lng);
        });
        mapInstance.current = map;
    }, [libLoaded]);

    // --- VISUAL RULER LOGIC ---
    useEffect(() => {
        if (!mapInstance.current || !prediction || !clickCoords || !window.L) return;
        const L = window.L;
        const distance = prediction.report?.dist_road;

        if (rulerInstance.current) rulerInstance.current.remove();
        if (distance === null || distance === undefined) return;

        if (distance < 10000) {
            const renderDist = distance === 0 ? 5 : distance;
            const sourcePos = [clickCoords.lat + (renderDist / 111320), clickCoords.lng];

            const polyline = L.polyline([[clickCoords.lat, clickCoords.lng], sourcePos], {
                color: '#d32f2f',
                dashArray: '8, 8',
                weight: 3
            }).addTo(mapInstance.current);

            polyline.bindTooltip(`${Math.round(distance)}m to Major Road`, {
                permanent: true,
                direction: 'top',
                opacity: 0.9,
                offset: [0, -10]
            });
            rulerInstance.current = polyline;
        }
    }, [prediction, clickCoords, libLoaded]);

    const handleInferenceRequest = async (lat, lng) => {
        setClickCoords({ lat, lng });
        setStatus("Running AI Explainability engine...");
        try {
            const wRes = await axios.get(
                `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lng}&appid=${API_KEY}&units=metric`
            );
            const w = wRes.data;

            const res = await axios.post('http://127.0.0.1:8000/predict', {
                lat, lon: lng,
                temp: w.main.temp, 
                pres: w.main.pressure,
                dewp: w.main.temp - ((100 - w.main.humidity) / 5),
                rain: w.rain ? w.rain['1h'] || 0 : 0,
                wspm: w.wind.speed,
                pm25_lag_1: 25
            });

            setPrediction(res.data);
            setStatus(`Analysis complete for ${w.name || 'selected coordinate'}`);
        } catch (err) {
            setStatus("Error: System offline or API timeout.");
        }
    };

    const handleSearch = async (e) => {
        if (e) e.preventDefault();
        if (!searchQuery.trim() || !mapInstance.current) return;

        setIsSearching(true);
        setStatus("Locating...");

        try {
            const response = await axios.get(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&countrycodes=be&limit=1`);
            
            if (response.data && response.data.length > 0) {
                const { lat, lon } = response.data[0];
                const latitude = parseFloat(lat);
                const longitude = parseFloat(lon);

                // Zoom to level 13 to see roads clearly without pixelating map labels
                mapInstance.current.flyTo([latitude, longitude], 13, { duration: 1.2 });
                handleInferenceRequest(latitude, longitude);
            } else {
                setStatus("Location not found in Belgium.");
            }
        } catch (error) {
            setStatus("Search error.");
        } finally {
            setIsSearching(false);
        }
    };

    return (
        <div style={{ display: 'flex', height: '100vh', width: '100vw', fontFamily: 'Inter, sans-serif', overflow: 'hidden' }}>
            {/* MAP SECTION */}
            <div style={{ flex: 2, position: 'relative' }}>
                <div ref={mapRef} style={{ height: '100%', width: '100%' }} />
                {!libLoaded && (
                    <div style={{ position: 'absolute', inset: 0, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                        Initializing Map Engine...
                    </div>
                )}
            </div>
            
            {/* SIDEBAR SECTION */}
            <div style={{ flex: 1, padding: '30px', background: '#fcfcfc', borderLeft: '1px solid #ddd', overflowY: 'auto' }}>
                <h1 style={{ fontSize: '1.6rem', color: '#333', fontWeight: 'bold', margin: 0 }}>{PROJECT_NAME}</h1>
                <p style={{ fontStyle: 'italic', color: '#777', marginTop: '8px', fontSize: '0.85rem' }}>{status}</p>
                
                {/* Search Bar */}
                <form onSubmit={handleSearch} style={{ display: 'flex', marginTop: '20px', gap: '8px' }}>
                    <div style={{ flex: 1, position: 'relative' }}>
                        <div style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', opacity: 0.4 }}>
                            <Icons.Search />
                        </div>
                        <input 
                            type="text" 
                            placeholder="Search places in Belgium..." 
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            disabled={isSearching}
                            style={{ 
                                width: '100%', 
                                padding: '10px 10px 10px 35px', 
                                borderRadius: '8px', 
                                border: '1px solid #ddd',
                                fontSize: '0.9rem',
                                outline: 'none'
                            }}
                        />
                    </div>
                    <button 
                        type="submit" 
                        disabled={isSearching}
                        style={{ 
                            padding: '10px 15px', 
                            background: '#3b82f6', 
                            color: 'white', 
                            border: 'none', 
                            borderRadius: '8px', 
                            cursor: isSearching ? 'not-allowed' : 'pointer',
                            fontSize: '0.9rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '5px'
                        }}
                    >
                        {isSearching ? '...' : <Icons.Navigation />}
                    </button>
                </form>

                <hr style={{ border: '0', borderTop: '1px solid #eee', margin: '20px 0' }} />
                
                {prediction ? (
                    <div className="fade-in">
                        <div style={{ 
                            padding: '30px', borderRadius: '24px', textAlign: 'center',
                            background: prediction.pm25 > 25 ? '#fff5f5' : '#f0fff4',
                            border: `2px solid ${prediction.pm25 > 25 ? '#feb2b2' : '#9ae6b4'}`,
                            boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
                        }}>
                            <h3 style={{ margin: 0, textTransform: 'uppercase', letterSpacing: '1px', fontSize: '0.9rem', color: '#555' }}>
                                {prediction.status}
                            </h3>
                            <h1 style={{ fontSize: '5rem', margin: '15px 0', fontWeight: '800', color: '#1a202c' }}>
                                {prediction.pm25}
                            </h1>
                            <p style={{ fontWeight: '600', color: '#4a5568', margin: 0 }}>Concentration (PM2.5)</p>
                        </div>

                        <div style={{ marginTop: '25px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
                                <Icons.Info />
                                <h4 style={{ color: '#334155', margin: 0, fontWeight: 'bold' }}>AI Explainability (XAI)</h4>
                            </div>
                            {prediction.insights && prediction.insights.map((item, i) => (
                                <div key={i} style={{ 
                                    marginBottom: '10px', 
                                    padding: '12px', 
                                    borderRadius: '12px', 
                                    background: item.impact === 'High' ? '#fff1f2' : '#f0fdf4', 
                                    borderLeft: `5px solid ${item.impact === 'High' ? '#e11d48' : '#22c55e'}`,
                                    boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                                }}>
                                    <strong style={{ fontSize: '0.9rem', color: '#2d3748' }}>{item.feature}</strong>
                                    <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#4a5568', lineHeight: '1.4' }}>{item.desc}</p>
                                </div>
                            ))}
                        </div>

                        <div style={{ marginTop: '25px', padding: '20px', background: 'white', borderRadius: '15px', border: '1px solid #eee' }}>
                            <h4 style={{ margin: '0 0 15px 0', fontWeight: 'bold', color: '#4a5568' }}>Hyper-Local GIS Data</h4>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.9rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <Icons.Car />
                                        <span>Major Road:</span>
                                    </div>
                                    <span style={{ fontWeight: 'bold' }}>{prediction.report?.dist_road}m</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <Icons.Tree />
                                        <span>Forest Sink:</span>
                                    </div>
                                    <span style={{ fontWeight: 'bold' }}>{prediction.report?.dist_forest}m</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <Icons.Factory />
                                        <span>Industrial Area:</span>
                                    </div>
                                    <span style={{ fontWeight: 'bold' }}>{prediction.report?.dist_industrial}m</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#cbd5e1', textAlign: 'center', marginTop: '100px' }}>
                        <Icons.MapPin opacity={0.2} />
                        <p style={{ fontSize: '0.9rem', lineHeight: '1.5' }}>Search for a place or click the map<br/>to generate a local report.</p>
                    </div>
                )}
            </div>
            <style>{`
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .fade-in { animation: fadeIn 0.5s ease-out; }
            `}</style>
        </div>
    );
}