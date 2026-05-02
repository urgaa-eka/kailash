import { useState, useEffect } from "react";

// Feature data with positions uniformly distributed (N, S, E, W and intermediates)
const FEATURES = [
  // Cardinal directions - North, East, South, West
  { name: "URGAA", yaw: 0, pitch: 90, color: "#00CC66", direction: "N" },
  { name: "Fleet Management", yaw: 90, pitch: 0, color: "#06B6D4", direction: "E" },
  { name: "Ignition", yaw: 180, pitch: -90, color: "#8B00FF", direction: "S" },
  { name: "Energy Management", yaw: -90, pitch: 0, color: "#22C55E", direction: "W" },
  
  // Upper hemisphere - NE, SE, SW, NW
  { name: "Service Tools", yaw: 45, pitch: 45, color: "#FF6600", direction: "NE" },
  { name: "Business Intelligence", yaw: 135, pitch: 45, color: "#A855F7", direction: "SE" },
  { name: "MG Partnership", yaw: -135, pitch: 45, color: "#0066FF", direction: "SW" },
  { name: "OEM Support", yaw: -45, pitch: 45, color: "#4ECDC4", direction: "NW" },
  
  // Lower hemisphere - NE, SE, SW, NW
  { name: "EV Charging", yaw: 45, pitch: -45, color: "#10B981", direction: "NE-Lower" },
  { name: "CPO Dashboard", yaw: 135, pitch: -45, color: "#3B82F6", direction: "SE-Lower" },
  { name: "Workshop Program", yaw: -135, pitch: -45, color: "#FFD93D", direction: "SW-Lower" },
  { name: "B2B Services", yaw: -45, pitch: -45, color: "#FF6B6B", direction: "NW-Lower" },
  
  { name: "Parts Network", yaw: 270, pitch: 0, color: "#FF006E", direction: "Additional" },
];

// Calculate 3D position on sphere
const calculateSpherePosition = (yaw, pitch, radius) => {
  const yawRad = (yaw * Math.PI) / 180;
  const pitchRad = (pitch * Math.PI) / 180;
  
  const x = radius * Math.cos(pitchRad) * Math.sin(yawRad);
  const y = -radius * Math.sin(pitchRad);
  const z = radius * Math.cos(pitchRad) * Math.cos(yawRad);
  
  return { x, y, z };
};

export const GlobeVisualization = () => {
  const [hoveredFeature, setHoveredFeature] = useState(null);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  
  // Globe radius adjusted for 500px container
  const globeRadius = 220;
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    const handleChange = (e) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  if (prefersReducedMotion) {
    return (
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center space-y-6 max-w-4xl px-6">
          <div className="text-lg font-semibold text-[hsl(var(--g4g-purple))]">
            Go4Garage Global Ecosystem
          </div>
          <div className="grid grid-cols-3 gap-4">
            {FEATURES.map((feature, i) => (
              <div key={i} className="space-y-2">
                <div 
                  className="px-4 py-2 rounded-full font-bold text-sm flex items-center gap-2 justify-center"
                  style={{ 
                    backgroundColor: feature.color,
                    color: '#FFFFFF'
                  }}
                >
                  {feature.name}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="absolute inset-0 pointer-events-none z-0 hidden lg:block"
      style={{ 
        perspective: '2000px',
        background: 'radial-gradient(circle at center, #1A0B2E 0%, #0A1628 50%, #000000 100%)',
        overflow: 'hidden'
      }}
      role="region"
      aria-label="3D Globe ecosystem visualization"
    >
      <div 
        className="absolute" 
        style={{ 
          width: '500px', 
          height: '500px',
          left: '25%',
          top: '50%',
          transform: 'translate(-50%, -50%)'
        }}
      >
        {/* Rotating Globe Container */}
        <div
          className="absolute inset-0 globe-container"
          style={{
            transformStyle: 'preserve-3d',
            animation: prefersReducedMotion || isPaused ? 'none' : 'rotate-globe 40s linear infinite',
            animationPlayState: isPaused ? 'paused' : 'running'
          }}
        >
          {/* Enhanced 3D Wireframe Globe */}
          <div
            className="absolute inset-0 rounded-full"
            style={{
              transformStyle: 'preserve-3d',
              position: 'relative',
              filter: 'drop-shadow(0 0 30px rgba(0, 217, 255, 0.5))'
            }}
          >
            {/* Main Globe Wireframe */}
            <svg className="absolute inset-0 w-full h-full" viewBox="0 0 700 700" style={{ opacity: 0.9 }}>
              <defs>
                <filter id="enhanced-cyan-glow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                
                <radialGradient id="globe-gradient">
                  <stop offset="0%" stopColor="#0A1628" stopOpacity="0.6" />
                  <stop offset="70%" stopColor="#0A1628" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#000000" stopOpacity="0" />
                </radialGradient>
              </defs>
              
              {/* Filled globe base */}
              <circle
                cx="350"
                cy="350"
                r="330"
                fill="url(#globe-gradient)"
                opacity="0.4"
              />
              
              {/* Latitude lines (horizontal circles) - More lines for density */}
              {[-80, -70, -60, -45, -30, -15, 0, 15, 30, 45, 60, 70, 80].map((lat, i) => (
                <ellipse
                  key={`lat-${i}`}
                  cx="350"
                  cy="350"
                  rx="330"
                  ry={330 * Math.cos((Math.abs(lat) * Math.PI) / 180)}
                  fill="none"
                  stroke={lat === 0 ? "rgba(0, 217, 255, 1)" : "rgba(0, 217, 255, 0.6)"}
                  strokeWidth={lat === 0 ? "3" : "2"}
                  filter="url(#enhanced-cyan-glow)"
                  transform={`translate(0, ${(lat / 90) * 330})`}
                />
              ))}
              
              {/* Longitude lines (vertical meridians) - Complete coverage */}
              {Array.from({ length: 36 }, (_, i) => i * 10).map(angle => {
                const rx = 330 * Math.abs(Math.cos((angle * Math.PI) / 180));
                const opacity = angle % 30 === 0 ? 0.8 : 0.5;
                const width = angle % 30 === 0 ? 2.5 : 1.8;
                return (
                  <ellipse
                    key={`lon-${angle}`}
                    cx="350"
                    cy="350"
                    rx={rx}
                    ry="330"
                    fill="none"
                    stroke={`rgba(0, 217, 255, ${opacity})`}
                    strokeWidth={width}
                    filter="url(#enhanced-cyan-glow)"
                    transform={`rotate(${angle} 350 350)`}
                  />
                );
              })}
              
              {/* Prime meridian */}
              <line
                x1="350"
                y1="20"
                x2="350"
                y2="680"
                stroke="rgba(0, 217, 255, 0.9)"
                strokeWidth="3"
                filter="url(#enhanced-cyan-glow)"
              />
              
              {/* Outer rim circle - Enhanced */}
              <circle
                cx="350"
                cy="350"
                r="330"
                fill="none"
                stroke="rgba(0, 217, 255, 0.9)"
                strokeWidth="3.5"
                filter="url(#enhanced-cyan-glow)"
              />
            </svg>
            
            {/* Ambient cyan glow pulses */}
            <div
              className="absolute inset-0 rounded-full"
              style={{
                background: 'radial-gradient(circle at center, rgba(0, 217, 255, 0.08), transparent 70%)',
                filter: 'blur(40px)',
                animation: prefersReducedMotion ? 'none' : 'cyan-pulse 4s ease-in-out infinite'
              }}
            />
          </div>

          {/* Connection Lines (SVG) */}
          <svg
            className="absolute inset-0 w-full h-full pointer-events-none"
            viewBox="0 0 700 700"
            style={{ transformStyle: 'preserve-3d' }}
          >
            {FEATURES.map((feature, idx) => {
              const pos = calculateSpherePosition(feature.yaw, feature.pitch, globeRadius);
              const centerX = 350;
              const centerY = 350;
              const endX = centerX + pos.x;
              const endY = centerY + pos.y;
              
              return (
                <line
                  key={`connection-${idx}`}
                  x1={centerX}
                  y1={centerY}
                  x2={endX}
                  y2={endY}
                  stroke={feature.color}
                  strokeWidth={hoveredFeature === idx ? "3" : "2"}
                  style={{ 
                    opacity: hoveredFeature === idx ? 0.9 : 0.4,
                    transition: 'all 0.3s ease',
                    filter: `drop-shadow(0 0 6px ${feature.color})`
                  }}
                />
              );
            })}
          </svg>

          {/* Feature Labels - Larger and more prominent */}
          {FEATURES.map((feature, idx) => {
            const pos = calculateSpherePosition(feature.yaw, feature.pitch, globeRadius);
            const isHovered = hoveredFeature === idx;
            
            return (
              <div
                key={`feature-${idx}`}
                className="absolute pointer-events-auto"
                style={{
                  left: '50%',
                  top: '50%',
                  transform: `translate3d(${pos.x}px, ${pos.y}px, ${pos.z}px)`,
                  transformStyle: 'preserve-3d',
                  zIndex: Math.round(100 + pos.z)
                }}
                onMouseEnter={() => {
                  setHoveredFeature(idx);
                  setIsPaused(true);
                }}
                onMouseLeave={() => {
                  setHoveredFeature(null);
                  setIsPaused(false);
                }}
              >
                {/* Feature Label Badge */}
                <div
                  className="whitespace-nowrap transition-all duration-300"
                  style={{
                    background: `linear-gradient(135deg, ${feature.color} 0%, ${feature.color}DD 100%)`,
                    color: '#FFFFFF',
                    padding: '12px 24px',
                    borderRadius: '28px',
                    fontFamily: 'Inter, Roboto, sans-serif',
                    fontWeight: 700,
                    fontSize: '16px',
                    letterSpacing: '0.4px',
                    boxShadow: isHovered 
                      ? `0 0 40px ${feature.color}DD, 0 10px 30px ${feature.color}90, 0 5px 15px rgba(0,0,0,0.5), inset 0 2px 4px rgba(255,255,255,0.3)`
                      : '0 8px 20px rgba(0, 0, 0, 0.4), 0 3px 10px rgba(0,0,0,0.3), inset 0 1px 3px rgba(255,255,255,0.2)',
                    zIndex: isHovered ? 1001 : 1000,
                    cursor: 'pointer',
                    opacity: hoveredFeature !== null && hoveredFeature !== idx ? 0.6 : 1,
                    transform: isHovered ? 'scale(1.15)' : 'scale(1)',
                    border: '2px solid rgba(255, 255, 255, 0.4)'
                  }}
                >
                  {feature.name}
                </div>

                {/* Tooltip on Hover */}
                {isHovered && (
                  <div
                    className="absolute whitespace-nowrap animate-modal-enter"
                    style={{
                      left: '50%',
                      top: 'calc(100% + 8px)',
                      transform: 'translateX(-50%)',
                      backgroundColor: 'rgba(255, 255, 255, 0.98)',
                      color: '#333',
                      padding: '8px 14px',
                      borderRadius: '10px',
                      fontSize: '12px',
                      fontWeight: 600,
                      boxShadow: '0 6px 16px rgba(0, 0, 0, 0.2)',
                      border: `2px solid ${feature.color}60`,
                      zIndex: 1002
                    }}
                  >
                    {feature.direction}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        {/* Center Mascot - Always Front Facing (Outside Rotating Container) - NON-NEGOTIABLE */}
        <div 
          className="absolute pointer-events-none" 
          style={{ 
            left: '50%', 
            top: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 150
          }}
        >
          <img
            src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/qaougk0e_MASCOT.png"
            alt="Go4Garage Mascot"
            className="object-contain"
            style={{ 
              width: '130px',
              height: '130px',
              filter: 'drop-shadow(0 12px 24px rgba(87, 6, 131, 0.4))',
              animation: 'none'
            }}
          />
        </div>

        {/* White Meridian and Parallel Lines for 3D Globe Effect */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            transformStyle: 'preserve-3d',
            animation: prefersReducedMotion || isPaused ? 'none' : 'rotate-white-globe 25s linear infinite'
          }}
        >
          {/* Meridian lines (vertical) */}
          {[0, 30, 60, 90, 120, 150].map((angle, i) => (
            <div
              key={`meridian-${i}`}
              className="absolute"
              style={{
                position: 'absolute',
                width: '500px',
                height: '500px',
                border: '2px solid rgba(255, 255, 255, 0.6)',
                borderRadius: '50%',
                top: '50%',
                left: '50%',
                transform: `translate(-50%, -50%) rotateY(${angle}deg)`,
                transformStyle: 'preserve-3d',
                boxShadow: '0 0 10px rgba(255, 255, 255, 0.4)'
              }}
            />
          ))}
          
          {/* Parallel lines (horizontal) */}
          {[0, 15, 30, 45, 60].map((offset, i) => {
            const size = 500 - (offset * 7.5);
            return (
              <div
                key={`parallel-${i}`}
                className="absolute"
                style={{
                  position: 'absolute',
                  width: `${size}px`,
                  height: `${size}px`,
                  border: '2px solid rgba(255, 255, 255, 0.6)',
                  borderRadius: '50%',
                  top: '50%',
                  left: '50%',
                  transform: `translate(-50%, -50%) rotateX(90deg) translateZ(${offset * 9}px)`,
                  transformStyle: 'preserve-3d',
                  boxShadow: '0 0 10px rgba(255, 255, 255, 0.4)'
                }}
              />
            );
          })}
        </div>

        {/* X and Y Axes */}
        <div className="absolute pointer-events-none" style={{ left: '50%', top: '50%', transform: 'translate(-50%, -50%)' }}>
          {/* X-axis (horizontal) */}
          <div
            style={{
              position: 'absolute',
              width: '500px',
              height: '2px',
              background: 'rgba(255, 255, 255, 0.7)',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              boxShadow: '0 0 12px rgba(255, 255, 255, 0.5)'
            }}
          />
          {/* Y-axis (vertical) */}
          <div
            style={{
              position: 'absolute',
              width: '2px',
              height: '500px',
              background: 'rgba(255, 255, 255, 0.7)',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              boxShadow: '0 0 12px rgba(255, 255, 255, 0.5)'
            }}
          />
        </div>

        {/* Sparkling Light Particles */}
        {Array.from({ length: 60 }).map((_, i) => {
          const angle = Math.random() * Math.PI * 2;
          const distance = Math.random() * 220 + 40;
          const x = Math.cos(angle) * distance;
          const y = Math.sin(angle) * distance;
          const size = Math.random() * 2 + 3; // Varied sizes 3-5px
          
          return (
            <div
              key={`sparkle-${i}`}
              className="absolute pointer-events-none animate-sparkle"
              style={{
                left: `calc(50% + ${x}px)`,
                top: `calc(50% + ${y}px)`,
                width: `${size}px`,
                height: `${size}px`,
                background: 'white',
                borderRadius: '50%',
                animationDelay: `${Math.random() * 2}s`,
                animationDuration: `${1.5 + Math.random() * 1.5}s`,
                boxShadow: '0 0 8px 2px rgba(255, 255, 255, 0.9)',
                zIndex: 100
              }}
            />
          );
        })}
      </div>

      {/* Screen reader announcements */}
      <div role="status" aria-live="polite" className="sr-only">
        {hoveredFeature !== null && `Viewing: ${FEATURES[hoveredFeature].name}`}
      </div>

      {/* Controls Panel */}
      <div 
        className="absolute bottom-4 right-4 pointer-events-auto flex flex-col gap-2 bg-white/95 backdrop-blur-md rounded-lg p-3 shadow-lg border"
        style={{ 
          borderColor: 'rgba(87, 6, 131, 0.2)',
          zIndex: 1000
        }}
      >
        <button
          onClick={() => setIsPaused(!isPaused)}
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold transition-all hover:scale-105"
          style={{
            backgroundColor: 'rgba(87, 6, 131, 0.1)',
            color: 'hsl(var(--g4g-purple))',
            border: '1px solid rgba(87, 6, 131, 0.2)'
          }}
          title={isPaused ? "Resume Rotation" : "Pause Rotation"}
        >
          <span className="text-base">{isPaused ? '▶️' : '⏸️'}</span>
          <span>{isPaused ? 'Resume' : 'Pause'}</span>
        </button>
      </div>
    </div>
  );
};

export default GlobeVisualization;
