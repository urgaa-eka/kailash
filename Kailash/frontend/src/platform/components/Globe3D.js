import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere, Text } from '@react-three/drei';
import * as THREE from 'three';

// Feature data with positions and colors
const FEATURES = [
  { name: "URGAA", color: "#00CC66", lat: 0, lon: 0 }, // North
  { name: "Business Intelligence", color: "#A855F7", lat: 0, lon: 90 }, // East
  { name: "Ignition", color: "#8B00FF", lat: 0, lon: 180 }, // South
  { name: "Fleet Management", color: "#06B6D4", lat: 0, lon: -90 }, // West
  { name: "Service Tools", color: "#FF6600", lat: 45, lon: 45 }, // NE
  { name: "Energy Management", color: "#22C55E", lat: 45, lon: 135 }, // SE
  { name: "MG Partnership", color: "#0066FF", lat: 45, lon: -135 }, // SW
  { name: "OEM Support", color: "#4ECDC4", lat: 45, lon: -45 }, // NW
  { name: "EV Charging", color: "#10B981", lat: -45, lon: 45 }, // NE lower
  { name: "CPO Dashboard", color: "#3B82F6", lat: -45, lon: 135 }, // SE lower
  { name: "Workshop Program", color: "#FFD93D", lat: -45, lon: -135 }, // SW lower
  { name: "B2B Services", color: "#FF6B6B", lat: -45, lon: -45 }, // NW lower
  { name: "Parts Network", color: "#FF006E", lat: 0, lon: 45 }, // Additional
];

// Convert lat/lon to 3D position
const latLonToVector3 = (lat, lon, radius) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  
  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);
  
  return new THREE.Vector3(x, y, z);
};

// 3D Globe with gridlines
function Globe3DModel({ hoveredFeature }) {
  const globeRef = useRef();
  const [isPaused, setIsPaused] = useState(false);
  
  // Rotate the globe
  useFrame((state, delta) => {
    if (globeRef.current && !isPaused) {
      globeRef.current.rotation.y += delta * 0.15;
    }
  });
  
  return (
    <group ref={globeRef} onPointerEnter={() => setIsPaused(true)} onPointerLeave={() => setIsPaused(false)}>
      {/* Main Globe Sphere with wireframe */}
      <Sphere args={[2.5, 64, 64]}>
        <meshBasicMaterial 
          color="#0A1628" 
          transparent 
          opacity={0.3} 
          wireframe={false}
        />
      </Sphere>
      
      {/* Wireframe Grid */}
      <Sphere args={[2.51, 32, 32]}>
        <meshBasicMaterial 
          color="#00D9FF" 
          wireframe 
          transparent 
          opacity={0.6}
        />
      </Sphere>
      
      {/* Glow effect */}
      <Sphere args={[2.6, 32, 32]}>
        <meshBasicMaterial 
          color="#00D9FF" 
          transparent 
          opacity={0.1} 
          side={THREE.BackSide}
        />
      </Sphere>
    </group>
  );
}

// Feature markers that stick to globe
function FeatureMarker({ feature, index, globeRadius, onHover }) {
  const markerRef = useRef();
  const [hovered, setHovered] = useState(false);
  
  const position = latLonToVector3(feature.lat, feature.lon, globeRadius);
  
  // Rotate with globe
  useFrame((state) => {
    if (markerRef.current) {
      // Calculate rotation to keep label facing camera
      const globeRotation = markerRef.current.parent.parent.rotation.y;
      markerRef.current.lookAt(state.camera.position);
    }
  });
  
  return (
    <group position={position} ref={markerRef}>
      {/* Feature Pin */}
      <mesh
        onPointerEnter={() => {
          setHovered(true);
          onHover(index);
        }}
        onPointerLeave={() => {
          setHovered(false);
          onHover(null);
        }}
      >
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshBasicMaterial color={feature.color} />
      </mesh>
      
      {/* Feature Label */}
      <Text
        position={[0.3, 0, 0]}
        fontSize={0.12}
        color={feature.color}
        anchorX="left"
        anchorY="middle"
        outlineWidth={0.01}
        outlineColor="#000000"
        font="https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiA.woff"
      >
        {feature.name}
      </Text>
      
      {/* Connection line to center */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={2}
            array={new Float32Array([0, 0, 0, -position.x, -position.y, -position.z])}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#00D9FF" transparent opacity={hovered ? 0.8 : 0.3} />
      </line>
    </group>
  );
}

// All features rotating with globe
function RotatingFeatures({ features, onHover }) {
  const groupRef = useRef();
  
  // Rotate features with globe
  useFrame((state, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.15;
    }
  });
  
  return (
    <group ref={groupRef}>
      {features.map((feature, index) => (
        <FeatureMarker
          key={index}
          feature={feature}
          index={index}
          globeRadius={2.6}
          onHover={onHover}
        />
      ))}
    </group>
  );
}

// Main component
export const Globe3D = () => {
  const [hoveredFeature, setHoveredFeature] = useState(null);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  
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
      className="absolute inset-0 flex items-center justify-center"
      style={{
        background: 'radial-gradient(circle at center, #1A0B2E 0%, #0A1628 50%, #000000 100%)',
      }}
    >
      {/* Central Mascot - Stationary */}
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
          className="w-36 h-36 object-contain"
          style={{ 
            filter: 'drop-shadow(0 10px 20px rgba(87, 6, 131, 0.25))'
          }}
        />
      </div>
      
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [0, 0, 8], fov: 50 }}
        style={{ width: '100%', height: '100%' }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        
        <Globe3DModel hoveredFeature={hoveredFeature} />
        <RotatingFeatures features={FEATURES} onHover={setHoveredFeature} />
        
        {/* Optional: Enable manual controls */}
        {/* <OrbitControls enableZoom={false} /> */}
      </Canvas>
      
      {/* Screen reader announcements */}
      <div role="status" aria-live="polite" className="sr-only">
        {hoveredFeature !== null && `Viewing: ${FEATURES[hoveredFeature].name}`}
      </div>
    </div>
  );
};

export default Globe3D;
