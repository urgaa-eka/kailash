import { useState, useEffect, useRef } from "react";
import { ChevronLeft, ChevronRight, Pause } from "lucide-react";

const TYPES = [
  { label: "Products", color: "hsl(var(--g4g-purple))", bg: "rgba(87, 6, 131, 0.1)" },
  { label: "Programs", color: "hsl(var(--g4g-green))", bg: "rgba(65, 126, 70, 0.1)" },
  { label: "Services", color: "hsl(var(--g4g-purple))", bg: "rgba(87, 6, 131, 0.1)" },
  { label: "Charging", color: "hsl(var(--g4g-bright-green))", bg: "rgba(13, 163, 78, 0.1)" },
  { label: "Intelligence", color: "hsl(var(--g4g-purple-light))", bg: "rgba(129, 114, 173, 0.1)" }
];

const ITEMS = [
  { label: "Ignition", type: 0, color: "hsl(var(--g4g-purple))", desc: "Efficiency & trust platform" },
  { label: "URGAA", type: 0, color: "hsl(var(--g4g-bright-green))", desc: "EV infrastructure ecosystem" },
  { label: "Service Tools", type: 0, color: "hsl(var(--g4g-green))", desc: "Advanced diagnostics suite" },
  { label: "MG Model", type: 1, color: "hsl(var(--g4g-purple))", desc: "Premium auto partnership" },
  { label: "OEM Support", type: 1, color: "hsl(var(--g4g-green))", desc: "Direct OEM collaboration" },
  { label: "Mandate Workshop", type: 1, color: "hsl(var(--g4g-orange))", desc: "Certified training programs" },
  { label: "B2B Services", type: 2, color: "hsl(var(--g4g-purple))", desc: "Enterprise fleet management" },
  { label: "Parts Distribution", type: 2, color: "hsl(var(--g4g-orange))", desc: "Authentic components" },
  { label: "EV Charging", type: 3, color: "hsl(var(--g4g-bright-green))", desc: "Complete charging ops" },
  { label: "CPO Dashboard", type: 4, color: "hsl(var(--g4g-purple))", desc: "Real-time analytics" },
  { label: "Energy Mgmt", type: 4, color: "hsl(var(--g4g-bright-green))", desc: "Smart optimization" },
  { label: "Fleet Mgmt", type: 4, color: "hsl(var(--g4g-green))", desc: "Vehicle control system" },
  { label: "Business Intel", type: 4, color: "hsl(var(--g4g-purple-light))", desc: "Financial analytics" }
];

const PHASES = { idle: 'idle', spinUp: 'spinUp', cruise: 'cruise', align: 'align', brake: 'brake', reveal: 'reveal', resume: 'resume' };
const TIMINGS = { spinUp: 900, cruise: 12000, align: 500, brake: 420, reveal: 1500, hold: 1200 };

export const DualRingWheel = () => {
  const [phase, setPhase] = useState(PHASES.idle);
  const [isPaused, setIsPaused] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [innerRotation, setInnerRotation] = useState(0);
  const [outerRotation, setOuterRotation] = useState(0);
  const [currentAlignment, setCurrentAlignment] = useState(0);
  const [hoveredItem, setHoveredItem] = useState(null);
  const [focusedItem, setFocusedItem] = useState(null);
  const [showLogo, setShowLogo] = useState(false);
  const [particles, setParticles] = useState([]);
  const [alignmentPulse, setAlignmentPulse] = useState(false);
  const [pulsingType, setPulsingType] = useState(null);
  const [debugMode, setDebugMode] = useState(false);
  const [debugKeyPresses, setDebugKeyPresses] = useState([]);
  const [cycleProgress, setCycleProgress] = useState(0);
  const [wheelScale, setWheelScale] = useState(1);
  
  const animationRef = useRef(null);
  const lastTimeRef = useRef(Date.now());
  const phaseStartRef = useRef(Date.now());
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const alignedItems = useRef(new Set());

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    const handleChange = (e) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Pause on tab visibility change
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        setIsPaused(true);
      } else if (!prefersReducedMotion) {
        setIsPaused(false);
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [prefersReducedMotion]);

  // Debug mode easter egg - Press 'D' three times
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key.toLowerCase() === 'd') {
        setDebugKeyPresses(prev => {
          const newPresses = [...prev, Date.now()].slice(-3);
          const timeDiff = newPresses[2] - newPresses[0];
          if (newPresses.length === 3 && timeDiff < 1000) {
            setDebugMode(prev => !prev);
            return [];
          }
          return newPresses;
        });
      }
    };
    window.addEventListener('keypress', handleKeyPress);
    return () => window.removeEventListener('keypress', handleKeyPress);
  }, []);

  // Calculate cycle progress
  useEffect(() => {
    const totalTypes = TYPES.length;
    const progress = (alignedItems.current.size / totalTypes) * 100;
    setCycleProgress(progress);
  }, [currentAlignment]);

  useEffect(() => {
    if (prefersReducedMotion || isPaused) {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      return;
    }

    const animate = () => {
      const now = Date.now();
      const delta = (now - lastTimeRef.current) / 1000;
      const phaseElapsed = now - phaseStartRef.current;
      lastTimeRef.current = now;

      switch (phase) {
        case PHASES.idle:
          if (phaseElapsed > 500) {
            setPhase(PHASES.spinUp);
            phaseStartRef.current = now;
          }
          break;

        case PHASES.spinUp:
          const t = Math.min(phaseElapsed / TIMINGS.spinUp, 1);
          const easeOut = 1 - Math.pow(1 - t, 3);
          setInnerRotation(prev => prev + delta * 8 * easeOut);
          setOuterRotation(prev => prev - delta * 12 * easeOut);
          
          if (phaseElapsed >= TIMINGS.spinUp) {
            setPhase(PHASES.cruise);
            phaseStartRef.current = now;
          }
          break;

        case PHASES.cruise:
          setInnerRotation(prev => (prev + delta * 8) % 360);
          setOuterRotation(prev => (prev - delta * 12) % 360);
          
          if (phaseElapsed >= TIMINGS.cruise) {
            setPhase(PHASES.align);
            phaseStartRef.current = now;
          }
          break;

        case PHASES.align:
          const alignT = Math.min(phaseElapsed / TIMINGS.align, 1);
          const easeSine = Math.sin(alignT * Math.PI / 2);
          
          if (phaseElapsed >= TIMINGS.align) {
            // 50ms pause at alignment moment for "snap" feeling
            setPhase(PHASES.brake);
            phaseStartRef.current = now + 50;
            setAlignmentPulse(true);
            setTimeout(() => setAlignmentPulse(false), 600);
            createDustBurst();
            alignedItems.current.add(currentAlignment);
          }
          break;

        case PHASES.brake:
          const brakeT = Math.min(phaseElapsed / TIMINGS.brake, 1);
          // Ease out back with overshoot
          const c = 1.70158;
          const easeBack = 1 - (Math.pow(1 - brakeT, 3) * ((c + 1) * (1 - brakeT) - c));
          
          if (phaseElapsed >= TIMINGS.brake) {
            setCurrentAlignment(prev => (prev + 1) % TYPES.length);
            
            // Check if full cycle complete
            if (alignedItems.current.size >= TYPES.length) {
              setPhase(PHASES.reveal);
              phaseStartRef.current = now;
              setShowLogo(true);
              alignedItems.current.clear();
            } else {
              setPhase(PHASES.resume);
              phaseStartRef.current = now;
            }
          }
          break;

        case PHASES.reveal:
          if (phaseElapsed >= TIMINGS.reveal + TIMINGS.hold) {
            setShowLogo(false);
            setPhase(PHASES.resume);
            phaseStartRef.current = now;
          }
          break;

        case PHASES.resume:
          if (phaseElapsed >= 500) {
            setPhase(PHASES.cruise);
            phaseStartRef.current = now;
          }
          break;

        default:
          break;
      }

      updateParticles(delta);
      animationRef.current = requestAnimationFrame(animate);
    };

    lastTimeRef.current = Date.now();
    phaseStartRef.current = Date.now();
    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [phase, prefersReducedMotion, isPaused, currentAlignment]);

  const createDustBurst = () => {
    const newParticles = [];
    for (let i = 0; i < 20; i++) {
      newParticles.push({
        x: 250 + (Math.random() - 0.5) * 40,
        y: 420 + Math.random() * 10,
        vx: (Math.random() - 0.5) * 60,
        vy: -Math.random() * 40 - 20,
        life: 0.35 + Math.random() * 0.15,
        maxLife: 0.35 + Math.random() * 0.15,
        size: 2 + Math.random() * 3
      });
    }
    setParticles(prev => [...prev, ...newParticles]);
  };

  const updateParticles = (delta) => {
    setParticles(prev => 
      prev
        .map(p => ({
          ...p,
          x: p.x + p.vx * delta,
          y: p.y + p.vy * delta,
          vy: p.vy + 100 * delta,
          life: p.life - delta
        }))
        .filter(p => p.life > 0)
    );
  };

  useEffect(() => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
      const alpha = p.life / p.maxLife;
      const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
      gradient.addColorStop(0, `rgba(180, 170, 160, ${alpha * 0.7})`);
      gradient.addColorStop(1, `rgba(180, 170, 160, 0)`);
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    });
  }, [particles]);

  const handleKeyDown = (e) => {
    if (!prefersReducedMotion) return;
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      setCurrentAlignment(prev => (prev + 1) % TYPES.length);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      setCurrentAlignment(prev => (prev - 1 + TYPES.length) % TYPES.length);
    }
  };

  const innerRadius = 90;
  const outerRadius = 210;
  const typeAngleStep = 360 / TYPES.length;
  const itemAngleStep = 360 / ITEMS.length;
  const activeItem = hoveredItem !== null ? hoveredItem : focusedItem;

  if (prefersReducedMotion) {
    return (
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center space-y-6">
          <div className="space-y-3">
            <div className="inline-block px-4 py-2 rounded-full" style={{ backgroundColor: TYPES[currentAlignment].bg }}>
              <div className="text-base font-bold" style={{ color: TYPES[currentAlignment].color }}>
                {TYPES[currentAlignment].label}
              </div>
            </div>
            <div className="space-y-2">
              {ITEMS.filter(i => i.type === currentAlignment).map((item, idx) => (
                <div key={idx} className="text-lg font-semibold" style={{ color: item.color }}>
                  {item.label}
                </div>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-4 justify-center">
            <button
              onClick={() => setCurrentAlignment(prev => (prev - 1 + TYPES.length) % TYPES.length)}
              className="w-12 h-12 rounded-full bg-[hsl(var(--g4g-purple))] text-white flex items-center justify-center hover:bg-[hsl(var(--g4g-purple-light))] transition-all hover:scale-110 focus:outline-2 focus:outline-[hsl(var(--g4g-bright-green))] focus:outline-offset-3"
              aria-label="Previous category"
            >
              <ChevronLeft className="w-6 h-6" strokeWidth={2} />
            </button>
            <button
              onClick={() => setCurrentAlignment(prev => (prev + 1) % TYPES.length)}
              className="w-12 h-12 rounded-full bg-[hsl(var(--g4g-purple))] text-white flex items-center justify-center hover:bg-[hsl(var(--g4g-purple-light))] transition-all hover:scale-110 focus:outline-2 focus:outline-[hsl(var(--g4g-bright-green))] focus:outline-offset-3"
              aria-label="Next category"
            >
              <ChevronRight className="w-6 h-6" strokeWidth={2} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="absolute inset-0 flex items-center justify-center pointer-events-none"
      role="region"
      aria-label="Dual ring showcase wheel"
    >
      <div 
        ref={containerRef}
        className="relative w-[550px] h-[550px] transition-transform duration-300 pointer-events-auto focus:outline-2 focus:outline-[hsl(var(--g4g-bright-green))] focus:outline-offset-4 focus:shadow-[0_0_0_6px_rgba(13,163,78,0.2)]" 
        style={{ transform: `scale(${wheelScale})` }}
        onMouseEnter={() => { setIsPaused(true); setWheelScale(1.02); }}
        onMouseLeave={() => { setIsPaused(false); setHoveredItem(null); setPulsingType(null); setWheelScale(1); }}
        onFocus={() => setIsPaused(true)}
        onBlur={() => { setIsPaused(false); setFocusedItem(null); }}
        onKeyDown={handleKeyDown}
        tabIndex={0}
      >
        {/* Pause Indicator */}
        {isPaused && !showLogo && (
          <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-white/95 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg z-30 animate-modal-enter">
            <div className="flex items-center gap-2 text-xs font-semibold text-[hsl(var(--g4g-purple))]">
              <Pause className="w-4 h-4" strokeWidth={2} />
              Motion Paused
            </div>
          </div>
        )}

        {/* Alignment Progress Indicator */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2 bg-white/90 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg z-20">
          {TYPES.map((type, i) => (
            <div
              key={i}
              className="transition-all duration-300"
              style={{
                width: i === currentAlignment ? '24px' : '8px',
                height: '8px',
                borderRadius: '4px',
                backgroundColor: i <= currentAlignment ? 'hsl(var(--g4g-bright-green))' : 'hsl(var(--g4g-gray))',
                transform: i === currentAlignment ? 'scale(1.2)' : 'scale(1)'
              }}
              title={type.label}
            />
          ))}
        </div>

        {/* Canvas for dust particles */}
        <canvas
          ref={canvasRef}
          width={550}
          height={550}
          className="absolute inset-0 pointer-events-none"
          style={{ mixBlendMode: 'multiply', opacity: 0.8 }}
        />

        {/* Logo Interlude */}
        {showLogo && (
          <div 
            className="absolute inset-0 flex items-center justify-center bg-white/98 backdrop-blur-md z-30"
            style={{ animation: 'modalEnter 1.2s ease-out forwards' }}
          >
            <div className="text-center space-y-6">
              <div className="relative inline-block">
                <div className="absolute inset-0 bg-gradient-radial from-[hsl(var(--g4g-bright-green)_/_0.3)] via-[hsl(var(--g4g-bright-green)_/_0.1)] to-transparent blur-2xl animate-pulse" />
                <img
                  src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/4ci0b4px_go4garage-header.png"
                  alt="Go4Garage"
                  className="relative h-24 w-auto"
                  style={{ filter: 'drop-shadow(0 0 30px rgba(13, 163, 78, 0.6))' }}
                />
              </div>
              <div className="space-y-2">
                <div className="text-lg font-bold bg-gradient-to-r from-[hsl(var(--g4g-purple))] via-[hsl(var(--g4g-orange))] to-[hsl(var(--g4g-bright-green))] bg-clip-text text-transparent">
                  India's Complete EV Infrastructure Solution
                </div>
                <div className="text-sm text-[hsl(var(--g4g-text-gray))]">
                  Powering {TYPES.length} Integrated Services
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SVG Dual Ring Wheel */}
        <svg width="550" height="550" viewBox="0 0 550 550" className="relative z-10">
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            <linearGradient id="innerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="hsl(var(--g4g-purple))" stopOpacity="0.3" />
              <stop offset="100%" stopColor="hsl(var(--g4g-purple-light))" stopOpacity="0.3" />
            </linearGradient>
            <linearGradient id="outerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="hsl(var(--g4g-green))" stopOpacity="0.25" />
              <stop offset="100%" stopColor="hsl(var(--g4g-bright-green))" stopOpacity="0.25" />
            </linearGradient>
          </defs>

          {/* Alignment pulse effect */}
          {alignmentPulse && (
            <circle
              cx="275"
              cy="275"
              r="100"
              fill="none"
              stroke="hsl(var(--g4g-bright-green))"
              strokeWidth="2"
              opacity="0"
            >
              <animate attributeName="r" from="80" to="220" dur="0.6s" />
              <animate attributeName="opacity" from="0.6" to="0" dur="0.6s" />
            </circle>
          )}

          {/* Center hub with depth */}
          <circle
            cx="275"
            cy="275"
            r="75"
            fill="white"
            stroke="url(#innerGradient)"
            strokeWidth="3"
            filter="drop-shadow(0 4px 12px rgba(87, 6, 131, 0.15))"
            style={{ pointerEvents: 'none' }}
          />
          <circle
            cx="275"
            cy="275"
            r="75"
            fill="none"
            stroke="white"
            strokeWidth="2"
            opacity="0.5"
            style={{ transform: 'translate(0, -2px)', pointerEvents: 'none' }}
          />

          {/* Inner Ring (Types) - Clockwise */}
          <g
            transform={`rotate(${innerRotation} 275 275)`}
            style={{ 
              transition: isPaused ? 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)' : 'none',
              transformOrigin: '275px 275px'
            }}
          >
            <circle
              cx="275"
              cy="275"
              r={innerRadius}
              fill="none"
              stroke="url(#innerGradient)"
              strokeWidth="20"
              filter="drop-shadow(0 2px 8px rgba(87, 6, 131, 0.1))"
              style={{ pointerEvents: 'none' }}
            />
            {TYPES.map((type, i) => {
              const angle = (i * typeAngleStep - 90) * (Math.PI / 180);
              const x = 275 + innerRadius * Math.cos(angle);
              const y = 275 + innerRadius * Math.sin(angle);
              const isActive = i === currentAlignment;
              const isPulsing = pulsingType === i;
              return (
                <g key={type.label}>
                  <circle 
                    cx={x} 
                    cy={y} 
                    r="10" 
                    fill={type.color}
                    filter={isActive ? "url(#glow)" : "none"}
                    style={{ transition: 'all 0.3s ease-out', pointerEvents: 'none' }}
                  />
                  <foreignObject
                    x={x - 40}
                    y={y - 30}
                    width="80"
                    height="20"
                    transform={`rotate(${-innerRotation} ${x} ${y})`}
                    className="pointer-events-none"
                  >
                    <div className="flex items-center justify-center">
                      <div
                        className={`px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap backdrop-blur-sm transition-all duration-300 ${isPulsing ? 'animate-pulse' : ''}`}
                        style={{
                          color: type.color,
                          backgroundColor: isActive ? type.bg : 'rgba(255, 255, 255, 0.9)',
                          boxShadow: isActive ? `0 2px 8px ${type.color.replace(')', ' / 0.3)')}` : '0 1px 3px rgba(0, 0, 0, 0.1)',
                          transform: isActive ? 'scale(1.15)' : isPulsing ? 'scale(1.1)' : 'scale(1)',
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
          </g>

          {/* Outer Ring (Items) - Counter-Clockwise */}
          <g
            transform={`rotate(${outerRotation} 275 275)`}
            style={{ 
              transition: isPaused ? 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)' : 'none',
              transformOrigin: '275px 275px'
            }}
          >
            <circle
              cx="275"
              cy="275"
              r={outerRadius}
              fill="none"
              stroke="url(#outerGradient)"
              strokeWidth="16"
              filter="drop-shadow(0 2px 8px rgba(65, 126, 70, 0.1))"
              style={{ pointerEvents: 'none' }}
            />
            {ITEMS.map((item, i) => {
              const angle = (i * itemAngleStep - 90) * (Math.PI / 180);
              const x = 275 + outerRadius * Math.cos(angle);
              const y = 275 + outerRadius * Math.sin(angle);
              const isHovered = activeItem === i;
              return (
                <g key={item.label}>
                  <circle
                    cx={x}
                    cy={y}
                    r={isHovered ? "12" : "9"}
                    fill={item.color}
                    opacity={isHovered ? 1 : 0.85}
                    filter={isHovered ? "url(#glow)" : "none"}
                    style={{
                      transition: 'all 0.3s ease-out',
                      cursor: 'pointer',
                      pointerEvents: 'none'
                    }}
                  />
                  {isHovered && (
                    <circle
                      cx={x}
                      cy={y}
                      r="20"
                      fill={item.color}
                      opacity="0.2"
                    >
                      <animate attributeName="r" from="12" to="24" dur="1s" repeatCount="indefinite" />
                      <animate attributeName="opacity" from="0.3" to="0" dur="1s" repeatCount="indefinite" />
                    </circle>
                  )}
                  <foreignObject
                    x={x - 45}
                    y={y + 12}
                    width="90"
                    height="30"
                    transform={`rotate(${-outerRotation} ${x} ${y})`}
                    className="pointer-events-auto"
                    onMouseEnter={() => { 
                      setHoveredItem(i); 
                      setPulsingType(item.type);
                      setTimeout(() => setPulsingType(null), 600);
                    }}
                    onMouseLeave={() => setHoveredItem(null)}
                    onFocus={() => setFocusedItem(i)}
                    onBlur={() => setFocusedItem(null)}
                    tabIndex={0}
                  >
                    <div className="flex items-center justify-center">
                      <div
                        className="px-2 py-1 rounded-full text-[11px] font-semibold whitespace-nowrap backdrop-blur-sm transition-all duration-300 cursor-pointer"
                        style={{
                          color: item.color,
                          backgroundColor: isHovered ? item.color.replace(')', ' / 0.15)') : 'rgba(255, 255, 255, 0.95)',
                          boxShadow: isHovered ? `0 4px 12px ${item.color.replace(')', ' / 0.4)')}` : '0 1px 3px rgba(0, 0, 0, 0.08)',
                          transform: isHovered ? 'scale(1.15) translateY(-2px)' : 'scale(1)',
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
          </g>

          {/* Radial pointer at 12 o'clock with pulse */}
          <g style={{ pointerEvents: 'none' }}>
            <line
              x1="275"
              y1="60"
              x2="275"
              y2="35"
              stroke="hsl(var(--g4g-bright-green))"
              strokeWidth="4"
              strokeLinecap="round"
              filter="url(#glow)"
            />
            <circle
              cx="275"
              cy="35"
              r="6"
              fill="hsl(var(--g4g-bright-green))"
              filter="url(#glow)"
            >
              <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite" />
            </circle>
          </g>
        </svg>

        {/* Center Mascot */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ top: '25px' }}>
          <img
            src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/qaougk0e_MASCOT.png"
            alt="Go4Garage Mascot"
            className="w-32 h-32 object-contain animate-mascot-bounce"
            style={{ filter: 'drop-shadow(0 10px 20px rgba(87, 6, 131, 0.25))' }}
          />
        </div>

        {/* Enhanced Tooltip */}
        {activeItem !== null && !showLogo && (
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
                boxShadow: `0 12px 32px rgba(0, 0, 0, 0.15), 0 0 0 1px ${ITEMS[activeItem].color.replace(')', ' / 0.2)')}`,
                borderColor: ITEMS[activeItem].color.replace(')', ' / 0.2)')
              }}
            >
              <div className="flex items-start gap-3">
                <div 
                  className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
                  style={{ backgroundColor: ITEMS[activeItem].color }}
                />
                <div>
                  <div className="text-base font-bold mb-1" style={{ color: ITEMS[activeItem].color }}>
                    {ITEMS[activeItem].label}
                  </div>
                  <div className="text-xs text-[hsl(var(--g4g-text-gray))] mb-1">
                    {ITEMS[activeItem].desc}
                  </div>
                  <div 
                    className="text-xs font-semibold"
                    style={{ color: TYPES[ITEMS[activeItem].type].color }}
                  >
                    {TYPES[ITEMS[activeItem].type].label} Category
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
                  borderColor: ITEMS[activeItem].color.replace(')', ' / 0.2)')
                }}
              />
            </div>
          </div>
        )}

        {/* Screen reader announcements */}
        <div role="status" aria-live="polite" className="sr-only">
          {phase === 'align' && `Now showcasing: ${TYPES[currentAlignment].label}`}
          {phase === 'reveal' && "Displaying Go4Garage complete services overview"}
        </div>

        {/* Progress indicator for screen readers */}
        <div 
          role="progressbar" 
          aria-valuenow={cycleProgress} 
          aria-valuemin="0" 
          aria-valuemax="100"
          aria-label="Service showcase progress"
          className="sr-only"
        >
          <span>{cycleProgress.toFixed(0)}% complete</span>
        </div>

        {/* Debug Mode */}
        {debugMode && (
          <div className="absolute top-20 right-4 bg-black/90 text-white p-4 rounded-xl font-mono text-xs space-y-1 backdrop-blur-sm animate-modal-enter z-40">
            <div className="font-bold text-[hsl(var(--g4g-bright-green))] mb-2">DEBUG MODE</div>
            <div>Phase: <span className="text-[hsl(var(--g4g-orange))]">{phase}</span></div>
            <div>Inner: <span className="text-[hsl(var(--g4g-purple-light))]">{innerRotation.toFixed(2)}°</span></div>
            <div>Outer: <span className="text-[hsl(var(--g4g-green-light))]">{outerRotation.toFixed(2)}°</span></div>
            <div>Aligned: <span className="text-[hsl(var(--g4g-bright-green))]">{alignedItems.current.size}/{TYPES.length}</span></div>
            <div>Progress: <span className="text-[hsl(var(--g4g-orange))]">{cycleProgress.toFixed(0)}%</span></div>
            <div>Paused: <span className={isPaused ? "text-yellow-400" : "text-green-400"}>{isPaused ? 'Yes' : 'No'}</span></div>
            <div className="text-[hsl(var(--g4g-gray))] text-[10px] mt-2">Press 'D' 3x to hide</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DualRingWheel;