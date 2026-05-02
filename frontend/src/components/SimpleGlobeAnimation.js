import { useEffect, useRef } from 'react';

const SimpleGlobeAnimation = () => {
  const globeContainerRef = useRef(null);

  useEffect(() => {
    // Create sparkling lights
    if (!globeContainerRef.current) return;

    const sparkleCount = 50;
    const globeContainer = globeContainerRef.current;

    for (let i = 0; i < sparkleCount; i++) {
      const sparkle = document.createElement('div');
      sparkle.className = 'sparkle';
      
      const angle = Math.random() * Math.PI * 2;
      const distance = Math.random() * 200;
      const x = Math.cos(angle) * distance + 200;
      const y = Math.sin(angle) * distance + 200;
      
      sparkle.style.left = x + 'px';
      sparkle.style.top = y + 'px';
      sparkle.style.animationDelay = Math.random() * 2 + 's';
      
      globeContainer.appendChild(sparkle);
    }

    // Cleanup
    return () => {
      const sparkles = globeContainer.querySelectorAll('.sparkle');
      sparkles.forEach(sparkle => sparkle.remove());
    };
  }, []);

  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <style>{`
        .globe-section {
          perspective: 1000px;
          position: relative;
          width: 400px;
          height: 400px;
        }

        .globe-container {
          position: relative;
          width: 100%;
          height: 100%;
          transform-style: preserve-3d;
        }

        .elephant-mascot-wrapper {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          z-index: 10;
          text-align: center;
          pointer-events: auto;
        }

        .elephant-mascot-wrapper img {
          animation: float 3s ease-in-out infinite;
          filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.3));
        }

        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }

        .globe {
          position: absolute;
          width: 100%;
          height: 100%;
          transform-style: preserve-3d;
          animation: rotateGlobe 20s linear infinite;
          top: 0;
          left: 0;
        }

        @keyframes rotateGlobe {
          from { transform: rotateY(0deg); }
          to { transform: rotateY(360deg); }
        }

        .axis {
          position: absolute;
          background: rgba(79, 172, 254, 0.6);
          box-shadow: 0 0 10px rgba(79, 172, 254, 0.4);
        }

        .x-axis {
          width: 100%;
          height: 2px;
          top: 50%;
          left: 0;
          transform: translateY(-50%);
        }

        .y-axis {
          width: 2px;
          height: 100%;
          left: 50%;
          top: 0;
          transform: translateX(-50%);
        }

        .meridian {
          position: absolute;
          width: 100%;
          height: 100%;
          border: 2px solid rgba(79, 172, 254, 0.5);
          border-radius: 50%;
          top: 0;
          left: 0;
          box-shadow: 0 0 10px rgba(79, 172, 254, 0.3);
        }

        .meridian:nth-child(1) { transform: rotateY(0deg); }
        .meridian:nth-child(2) { transform: rotateY(30deg); }
        .meridian:nth-child(3) { transform: rotateY(60deg); }
        .meridian:nth-child(4) { transform: rotateY(90deg); }
        .meridian:nth-child(5) { transform: rotateY(120deg); }
        .meridian:nth-child(6) { transform: rotateY(150deg); }

        .parallel {
          position: absolute;
          border: 2px solid rgba(79, 172, 254, 0.5);
          border-radius: 50%;
          left: 50%;
          transform: translateX(-50%) rotateX(90deg);
          box-shadow: 0 0 10px rgba(79, 172, 254, 0.3);
        }

        .parallel:nth-child(7) { 
          width: 100%; 
          height: 100%; 
          top: 0; 
        }
        .parallel:nth-child(8) { 
          width: 80%; 
          height: 80%; 
          top: 10%; 
        }
        .parallel:nth-child(9) { 
          width: 60%; 
          height: 60%; 
          top: 20%; 
        }
        .parallel:nth-child(10) { 
          width: 40%; 
          height: 40%; 
          top: 30%; 
        }

        .sparkle {
          position: absolute;
          width: 4px;
          height: 4px;
          background: rgba(79, 172, 254, 1);
          border-radius: 50%;
          animation: sparkle 2s ease-in-out infinite;
          box-shadow: 0 0 10px 2px rgba(79, 172, 254, 0.8);
        }

        @keyframes sparkle {
          0%, 100% { 
            opacity: 0;
            transform: scale(0);
          }
          50% { 
            opacity: 1;
            transform: scale(1.5);
          }
        }

        .features {
          position: absolute;
          width: 100%;
          height: 100%;
          top: 0;
          left: 0;
          transform-style: preserve-3d;
          animation: rotateFeatures 15s linear infinite;
        }

        @keyframes rotateFeatures {
          from { transform: rotateY(0deg); }
          to { transform: rotateY(360deg); }
        }

        .feature-item {
          position: absolute;
          background: rgba(255, 255, 255, 0.9);
          padding: 15px 25px;
          border-radius: 30px;
          font-weight: 600;
          color: #4facfe;
          box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
          white-space: nowrap;
          animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }

        .feature-item:nth-child(1) {
          top: 10%;
          left: 50%;
          transform: translateX(-50%) translateZ(200px);
          animation-delay: 0s;
        }

        .feature-item:nth-child(2) {
          top: 50%;
          right: -10%;
          transform: translateY(-50%) translateZ(200px);
          animation-delay: 0.3s;
        }

        .feature-item:nth-child(3) {
          bottom: 10%;
          left: 50%;
          transform: translateX(-50%) translateZ(200px);
          animation-delay: 0.6s;
        }

        .feature-item:nth-child(4) {
          top: 50%;
          left: -10%;
          transform: translateY(-50%) translateZ(200px);
          animation-delay: 0.9s;
        }
      `}</style>

      <div className="globe-section">
        <div className="globe-container" ref={globeContainerRef}>
          {/* Axes */}
          <div className="axis x-axis"></div>
          <div className="axis y-axis"></div>
          
          {/* Elephant Mascot Wrapper */}
          <div className="elephant-mascot-wrapper">
            <img
              src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/qaougk0e_MASCOT.png"
              alt="Go4Garage Mascot"
              className="w-32 h-32 object-contain"
            />
          </div>
          
          {/* Rotating Globe */}
          <div className="globe">
            <div className="meridian"></div>
            <div className="meridian"></div>
            <div className="meridian"></div>
            <div className="meridian"></div>
            <div className="meridian"></div>
            <div className="meridian"></div>
            <div className="parallel"></div>
            <div className="parallel"></div>
            <div className="parallel"></div>
            <div className="parallel"></div>
          </div>
          
          {/* Rotating Features */}
          <div className="features">
            <div className="feature-item"> Fast & Efficient</div>
            <div className="feature-item">Secure</div>
            <div className="feature-item"> Real-time</div>
            <div className="feature-item"> Accurate</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleGlobeAnimation;
