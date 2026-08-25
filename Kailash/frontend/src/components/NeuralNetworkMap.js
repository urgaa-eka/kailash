import { useState, useEffect, useRef } from "react";
import { 
  Pause, Zap, Building2, Wrench, Car, Users, GraduationCap, 
  Briefcase, Package, Plug, BarChart3, Battery, Truck, PieChart 
} from "lucide-react";

const TYPES = [
  { label: "Products", color: "hsl(var(--g4g-purple))", bg: "rgba(87, 6, 131, 0.1)" },
  { label: "Programs", color: "hsl(var(--g4g-green))", bg: "rgba(65, 126, 70, 0.1)" },
  { label: "Services", color: "hsl(var(--g4g-purple))", bg: "rgba(87, 6, 131, 0.1)" },
  { label: "Charging", color: "hsl(var(--g4g-bright-green))", bg: "rgba(13, 163, 78, 0.1)" },
  { label: "Intelligence", color: "hsl(var(--g4g-purple-light))", bg: "rgba(129, 114, 173, 0.1)" }
];

const ITEMS = [
  { label: "Ignition", type: 0, color: "#8B00FF", desc: "Efficiency & trust platform", icon: "Zap" },
  { label: "URGAA", type: 0, color: "#00CC66", desc: "EV infrastructure ecosystem", icon: "Building2" },
  { label: "Service Tools", type: 0, color: "#FF6600", desc: "Advanced diagnostics suite", icon: "Wrench" },
  { label: "MG Model Partnership", type: 1, color: "#0066FF", desc: "Premium auto partnership", icon: "Car" },
  { label: "OEM Manufacturer Support", type: 1, color: "#4ECDC4", desc: "Direct OEM collaboration", icon: "Users" },
  { label: "Mandate Workshop Program", type: 1, color: "#FFD93D", desc: "Certified training programs", icon: "GraduationCap" },
  { label: "Business-to-Business Services", type: 2, color: "#FF006E", desc: "Enterprise fleet management", icon: "Briefcase" },
  { label: "Parts Distribution Network", type: 2, color: "#FF6B6B", desc: "Authentic components", icon: "Package" },
  { label: "Electric Vehicle Charging", type: 3, color: "#00CC66", desc: "Complete charging ops", icon: "Plug" },
  { label: "Charging Point Operator Dashboard", type: 4, color: "#3A86FF", desc: "Real-time analytics", icon: "BarChart3" },
  { label: "Energy Management System", type: 4, color: "#A8E6CF", desc: "Smart optimization", icon: "Battery" },
  { label: "Fleet Management System", type: 4, color: "#4ECDC4", desc: "Vehicle control system", icon: "Truck" },
  { label: "Business Intelligence Analytics", type: 4, color: "#8B00FF", desc: "Financial analytics", icon: "PieChart" }
];

// Icon mapping
const getIconComponent = (iconName) => {
  const icons = {
    Zap, Building2, Wrench, Car, Users, GraduationCap,
    Briefcase, Package, Plug, BarChart3, Battery, Truck, PieChart
  };
  return icons[iconName] || Zap;
};

// Position calculations for organic layout
const getNodePosition = (index, total, radius, centerX, centerY) => {
  const angle = (index / total) * Math.PI * 2 - Math.PI / 2;
  return {
    x: centerX + Math.cos(angle) * radius,
    y: centerY + Math.sin(angle) * radius
  };
};

export const NeuralNetworkMap = () => {
  const [isPaused, setIsPaused] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [hoveredType, setHoveredType] = useState(null);
  const [pulsePhase, setPulsePhase] = useState(0);
  const [aiThinking, setAiThinking] = useState(false);
  const [particles, setParticles] = useState([]);
  const [wheelScale, setWheelScale] = useState(1);
  
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const lastTimeRef = useRef(Date.now());

  // Detect reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    const handleChange = (e) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Position nodes organically with better spacing
  const centerX = 275;
  const centerY = 275;
  const typeRadius = 100;
  const itemBaseRadius = 200;

  const typePositions = TYPES.map((_, i) => 
    getNodePosition(i, TYPES.length, typeRadius, centerX, centerY)
  );

  // Group items by type and position them with better distribution
  const itemPositions = ITEMS.map((item) => {
    const typePos = typePositions[item.type];
    const itemsOfType = ITEMS.filter(it => it.type === item.type);
    const indexInType = itemsOfType.findIndex(it => it.label === item.label);
    
    // Calculate angle with better spread
    const baseAngle = (item.type / TYPES.length) * Math.PI * 2 - Math.PI / 2;
    const spreadAngle = (indexInType - (itemsOfType.length - 1) / 2) * 0.4;
    const finalAngle = baseAngle + spreadAngle;
    
    // Vary radius for less overlap
    const radiusVariation = 15 * (indexInType % 2 === 0 ? 1 : -1);
    const finalRadius = itemBaseRadius + radiusVariation;
    
    return {
      x: centerX + Math.cos(finalAngle) * finalRadius,
      y: centerY + Math.sin(finalAngle) * finalRadius
    };
  });

  // Pulsing animation
  useEffect(() => {
    if (prefersReducedMotion || isPaused) return;
    
    const interval = setInterval(() => {
      setPulsePhase(prev => (prev + 0.05) % (Math.PI * 2));
    }, 50);
    
    return () => clearInterval(interval);
  }, [prefersReducedMotion, isPaused]);

  // AI Thinking animation
  useEffect(() => {
    if (prefersReducedMotion) return;
    
    const thinkingInterval = setInterval(() => {
      setAiThinking(true);
      setTimeout(() => setAiThinking(false), 2000);
    }, 15000);
    
    return () => clearInterval(thinkingInterval);
  }, [prefersReducedMotion]);

  // Particle system
  useEffect(() => {
    if (prefersReducedMotion || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Create initial particles
    const initialParticles = [];
    ITEMS.forEach((item, itemIdx) => {
      const typePos = typePositions[item.type];
      const itemPos = itemPositions[itemIdx];
      
      for (let i = 0; i < 2; i++) {
        initialParticles.push({
          fromX: typePos.x,
          fromY: typePos.y,
          toX: itemPos.x,
          toY: itemPos.y,
          progress: Math.random(),
          speed: 0.003 + Math.random() * 0.002,
          color: item.color,
          size: 2 + Math.random() * 1,
          itemIdx,
          typeIdx: item.type
        });
      }
    });
    setParticles(initialParticles);

    const animate = () => {
      const now = Date.now();
      const delta = (now - lastTimeRef.current) / 1000;
      lastTimeRef.current = now;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      setParticles(prevParticles => 
        prevParticles.map(p => {
          let newProgress = p.progress + (isPaused ? 0 : p.speed);
          if (newProgress > 1) newProgress = 0;

          // Bezier curve interpolation
          const t = newProgress;
          const controlX = (p.fromX + p.toX) / 2;
          const controlY = (p.fromY + p.toY) / 2 - 30;
          
          const x = Math.pow(1-t, 2) * p.fromX + 2*(1-t)*t * controlX + Math.pow(t, 2) * p.toX;
          const y = Math.pow(1-t, 2) * p.fromY + 2*(1-t)*t * controlY + Math.pow(t, 2) * p.toY;

          // Draw particle - use simple color based on type
          const particleColors = {
            0: 'rgba(87, 6, 131, 0.8)',    // Purple
            1: 'rgba(65, 126, 70, 0.8)',   // Green
            2: 'rgba(87, 6, 131, 0.8)',    // Purple
            3: 'rgba(13, 163, 78, 0.8)',   // Bright Green
            4: 'rgba(129, 114, 173, 0.8)'  // Purple Light
          };
          
          const baseColor = particleColors[p.typeIdx] || 'rgba(87, 6, 131, 0.8)';
          const gradient = ctx.createRadialGradient(x, y, 0, x, y, p.size);
          gradient.addColorStop(0, baseColor);
          gradient.addColorStop(1, baseColor.replace(/[\d.]+\)$/, '0)'));
          
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(x, y, p.size, 0, Math.PI * 2);
          ctx.fill();

          return { ...p, progress: newProgress };
        })
      );

      animationRef.current = requestAnimationFrame(animate);
    };

    lastTimeRef.current = Date.now();
    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [isPaused, prefersReducedMotion]);

  // Bezier curve path generator
  const getBezierPath = (x1, y1, x2, y2) => {
    const controlX = (x1 + x2) / 2;
    const controlY = (y1 + y2) / 2 - 30;
    return `M ${x1} ${y1} Q ${controlX} ${controlY}, ${x2} ${y2}`;
  };

  const activeNode = hoveredNode !== null ? hoveredNode : null;

  if (prefersReducedMotion) {
    return (
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center space-y-6 max-w-2xl">
          <div className="text-lg font-semibold text-[hsl(var(--g4g-purple))]">
            Go4Garage Ecosystem
          </div>
          <div className="grid grid-cols-5 gap-4">
            {TYPES.map((type, i) => (
              <div key={i} className="space-y-2">
                <div className="px-3 py-2 rounded-lg font-bold text-sm" style={{ 
                  color: type.color, 
                  backgroundColor: type.bg 
                }}>
                  {type.label}
                </div>
                <div className="space-y-1">
                  {ITEMS.filter(item => item.type === i).map((item, idx) => (
                    <div key={idx} className="text-xs px-2 py-1" style={{ color: item.color }}>
                      {item.label}
                    </div>
                  ))}
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
      className="absolute inset-0 flex items-center pointer-events-none"
      style={{ justifyContent: 'flex-start', paddingLeft: 'calc((100vw - 450px - 550px) / 4)' }}
      role="region"
      aria-label="Neural network ecosystem map"
    >
      <div 
        className="relative w-[550px] h-[550px] transition-transform duration-300 pointer-events-auto" 
        style={{ transform: `scale(${wheelScale})` }}
        onMouseEnter={() => { setIsPaused(true); setWheelScale(1.02); }}
        onMouseLeave={() => { setIsPaused(false); setHoveredNode(null); setHoveredType(null); setWheelScale(1); }}
        tabIndex={0}
      >
        {/* Pause Indicator */}
        {isPaused && (
          <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-white/95 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg z-30 animate-modal-enter pointer-events-none">
            <div className="flex items-center gap-2 text-xs font-semibold text-[hsl(var(--g4g-purple))]">
              <Pause className="w-4 h-4" strokeWidth={2} />
              Network Paused
            </div>
          </div>
        )}

        {/* Canvas for particles */}
        <canvas
          ref={canvasRef}
          width={550}
          height={550}
          className="absolute inset-0 pointer-events-none"
          style={{ mixBlendMode: 'screen', opacity: 0.6 }}
        />

        {/* SVG Network */}
        <svg width="550" height="550" viewBox="0 0 550 550" className="relative z-10">
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="hsl(var(--g4g-purple))" stopOpacity="0.3" />
              <stop offset="50%" stopColor="hsl(var(--g4g-bright-green))" stopOpacity="0.5" />
              <stop offset="100%" stopColor="hsl(var(--g4g-green))" stopOpacity="0.3" />
            </linearGradient>
          </defs>

          {/* Subtle background grid */}
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <circle cx="1" cy="1" r="0.5" fill="hsl(var(--g4g-purple))" opacity="0.05" />
          </pattern>
          <rect width="550" height="550" fill="url(#grid)" />

          {/* Neural connections */}
          {ITEMS.map((item, itemIdx) => {
            const typePos = typePositions[item.type];
            const itemPos = itemPositions[itemIdx];
            const isHighlighted = hoveredType === item.type || hoveredNode === itemIdx || aiThinking;
            
            return (
              <path
                key={`connection-${itemIdx}`}
                d={getBezierPath(typePos.x, typePos.y, itemPos.x, itemPos.y)}
                stroke={isHighlighted ? item.color : "url(#connectionGradient)"}
                strokeWidth={isHighlighted ? "2" : "1"}
                fill="none"
                opacity={isHighlighted ? 0.8 : 0.3}
                style={{ 
                  transition: 'all 0.3s ease-out',
                  pointerEvents: 'none'
                }}
              />
            );
          })}

          {/* Type nodes (inner circle) */}
          {TYPES.map((type, i) => {
            const pos = typePositions[i];
            const isActive = hoveredType === i;
            const pulseSize = 2 + Math.sin(pulsePhase) * 1;
            
            return (
              <g key={`type-${i}`}>
                {/* Pulsing outer ring */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={20 + pulseSize}
                  fill="none"
                  stroke={type.color}
                  strokeWidth="1"
                  opacity="0.3"
                  style={{ pointerEvents: 'none' }}
                />
                
                {/* Main node */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="18"
                  fill={type.bg}
                  stroke={type.color}
                  strokeWidth="2"
                  filter={isActive ? "url(#glow)" : "none"}
                  style={{ 
                    transition: 'all 0.3s ease-out',
                    cursor: 'pointer',
                    pointerEvents: 'none'
                  }}
                />
                
                {/* Type label */}
                <foreignObject
                  x={pos.x - 50}
                  y={pos.y + 28}
                  width="100"
                  height="30"
                  className="pointer-events-auto"
                  onMouseEnter={() => setHoveredType(i)}
                  onMouseLeave={() => setHoveredType(null)}
                >
                  <div className="flex items-center justify-center">
                    <div
                      className="px-3 py-1 rounded-full text-[11px] font-bold whitespace-nowrap backdrop-blur-sm transition-all duration-300 cursor-pointer"
                      style={{
                        color: type.color,
                        backgroundColor: isActive ? type.color.replace(')', ' / 0.2)') : 'rgba(255, 255, 255, 0.95)',
                        boxShadow: isActive ? `0 4px 12px ${type.color.replace(')', ' / 0.4)')}` : '0 1px 3px rgba(0, 0, 0, 0.08)',
                        transform: isActive ? 'scale(1.1) translateY(-2px)' : 'scale(1)',
                        textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                      }}
                    >
                      {type.label}
                    </div>
                  </div>
                </foreignObject>
              </g>
            );
          })}

          {/* Item nodes (outer circle) */}
          {ITEMS.map((item, itemIdx) => {
            const pos = itemPositions[itemIdx];
            const isHovered = activeNode === itemIdx;
            const isTypeActive = hoveredType === item.type;
            const pulseSize = isTypeActive ? 2 : 0;
            const IconComponent = getIconComponent(item.icon);
            
            return (
              <g key={`item-${itemIdx}`}>
                {/* Pulsing ring on hover */}
                {(isHovered || isTypeActive) && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r="28"
                    fill="none"
                    stroke={item.color}
                    strokeWidth="2"
                    opacity="0.4"
                  >
                    <animate attributeName="r" from="20" to="32" dur="1.5s" repeatCount="indefinite" />
                    <animate attributeName="opacity" from="0.4" to="0" dur="1.5s" repeatCount="indefinite" />
                  </circle>
                )}
                
                {/* Circular Icon Container */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={isHovered ? "22" : "20"}
                  fill={item.color}
                  opacity={isHovered ? 0.2 : 0.15}
                  filter={isHovered ? "url(#glow)" : "none"}
                  style={{
                    transition: 'all 0.3s ease-out',
                    cursor: 'pointer',
                    pointerEvents: 'none'
                  }}
                />
                
                {/* Icon in Circle */}
                <foreignObject
                  x={pos.x - 12}
                  y={pos.y - 12}
                  width="24"
                  height="24"
                  className="pointer-events-none"
                >
                  <div className="flex items-center justify-center w-full h-full">
                    <IconComponent 
                      size={isHovered ? 16 : 14} 
                      style={{ color: item.color }}
                      strokeWidth={2.5}
                      className="transition-all duration-300"
                    />
                  </div>
                </foreignObject>
                
                {/* Item label with new typography */}
                <foreignObject
                  x={pos.x - 75}
                  y={pos.y + 26}
                  width="150"
                  height="50"
                  className="pointer-events-auto"
                  onMouseEnter={() => setHoveredNode(itemIdx)}
                  onMouseLeave={() => setHoveredNode(null)}
                  tabIndex={0}
                >
                  <div className="flex items-center justify-center">
                    <div
                      className="px-3 py-1.5 rounded-lg backdrop-blur-sm transition-all duration-300 cursor-pointer text-center"
                      style={{
                        color: item.color,
                        backgroundColor: isHovered ? `${item.color}1A` : 'rgba(255, 255, 255, 0.95)',
                        boxShadow: isHovered ? `0 4px 12px ${item.color}40` : '0 1px 3px rgba(0, 0, 0, 0.08)',
                        transform: isHovered ? 'scale(1.08) translateY(-2px)' : 'scale(1)',
                        fontFamily: 'Inter, Roboto, -apple-system, system-ui, sans-serif',
                        fontWeight: 700,
                        fontSize: '11px',
                        letterSpacing: '0.5px',
                        lineHeight: 1.4,
                        textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                      }}
                    >
                      {item.label}
                    </div>
                  </div>
                </foreignObject>
              </g>
            );
          })}
        </svg>

        {/* Center Mascot - Static */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ top: '25px' }}>
          <img
            src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/qaougk0e_MASCOT.png"
            alt="Go4Garage Mascot"
            className="w-32 h-32 object-contain"
            style={{ filter: 'drop-shadow(0 10px 20px rgba(87, 6, 131, 0.25))' }}
          />
        </div>

        {/* Tooltip */}
        {activeNode !== null && (
          <div
            className="absolute pointer-events-none z-30 animate-modal-enter"
            style={{
              left: '50%',
              top: '30px',
              transform: 'translateX(-50%)'
            }}
          >
            <div 
              className="bg-white/98 backdrop-blur-md rounded-xl shadow-2xl p-4 border"
              style={{ 
                boxShadow: `0 12px 32px rgba(0, 0, 0, 0.15), 0 0 0 1px ${ITEMS[activeNode].color.replace(')', ' / 0.2)')}`,
                borderColor: ITEMS[activeNode].color.replace(')', ' / 0.2)')
              }}
            >
              <div className="flex items-start gap-3">
                <div 
                  className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
                  style={{ backgroundColor: ITEMS[activeNode].color }}
                />
                <div>
                  <div className="text-base font-bold mb-1" style={{ color: ITEMS[activeNode].color }}>
                    {ITEMS[activeNode].label}
                  </div>
                  <div className="text-xs text-[hsl(var(--g4g-text-gray))] mb-1">
                    {ITEMS[activeNode].desc}
                  </div>
                  <div 
                    className="text-xs font-semibold"
                    style={{ color: TYPES[ITEMS[activeNode].type].color }}
                  >
                    {TYPES[ITEMS[activeNode].type].label} Category
                  </div>
                </div>
              </div>
              {/* Caret */}
              <div 
                className="absolute w-3 h-3 bg-white rotate-45 border-l border-t"
                style={{
                  bottom: '-6px',
                  left: '50%',
                  transform: 'translateX(-50%) rotate(45deg)',
                  borderColor: ITEMS[activeNode].color.replace(')', ' / 0.2)')
                }}
              />
            </div>
          </div>
        )}

        {/* Screen reader announcements */}
        <div role="status" aria-live="polite" className="sr-only">
          {hoveredNode !== null && `Viewing: ${ITEMS[hoveredNode].label}`}
          {hoveredType !== null && `Category: ${TYPES[hoveredType].label}`}
        </div>
      </div>
    </div>
  );
};
