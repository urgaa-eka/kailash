import { useState, useRef, useEffect, useCallback } from "react";

export const VideoBackground = () => {
  const videoRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const videoSrc = "/kailash_video_optimized.mp4";

  const attemptPlay = useCallback(async () => {
    const video = videoRef.current;
    if (!video) return;
    
    try {
      await video.play();
      setIsLoaded(true);
    } catch (error) {
      console.log("Video autoplay failed:", error);
      // Still show video even if autoplay fails
      setIsLoaded(true);
    }
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleCanPlay = () => {
      console.log("Video can play");
      setIsLoaded(true);
      attemptPlay();
    };

    const handleError = (e) => {
      console.error("Video error:", e);
      setHasError(true);
    };

    const handleLoadedMetadata = () => {
      console.log("Video metadata loaded");
      // Show video as soon as metadata is loaded
      setIsLoaded(true);
      attemptPlay();
    };

    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('error', handleError);

    // Force show video after 2 seconds regardless of state (for slow networks)
    const forceShowTimeout = setTimeout(() => {
      setIsLoaded(true);
      attemptPlay();
    }, 2000);

    return () => {
      clearTimeout(forceShowTimeout);
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('error', handleError);
    };
  }, [attemptPlay]);

  // Fallback gradient if video fails
  if (hasError) {
    return (
      <div 
        className="absolute inset-0 z-0"
        style={{
          background: `
            radial-gradient(ellipse at center, rgba(129, 114, 173, 0.15) 0%, transparent 70%),
            radial-gradient(ellipse at 20% 80%, rgba(76, 175, 80, 0.1) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(87, 6, 131, 0.1) 0%, transparent 50%),
            linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #0d0d1a 100%)
          `
        }}
      />
    );
  }

  return (
    <>
      {/* Dark overlay for better readability - only on sides, not top/bottom */}
      <div 
        className="absolute inset-0 z-[1] pointer-events-none"
        style={{
          background: 'linear-gradient(to right, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.05) 40%, rgba(0,0,0,0.3) 100%)'
        }}
      />
      
      {/* Loading state with elegant transition */}
      {!isLoaded && (
        <div 
          className="absolute inset-0 z-0 flex items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #0d0d1a 100%)'
          }}
        >
          {/* Animated loading orbs */}
          <div className="relative w-32 h-32">
            <div 
              className="absolute inset-0 rounded-full animate-ping opacity-20"
              style={{ background: 'linear-gradient(135deg, #8172AD, #4CAF50)' }}
            />
            <div 
              className="absolute inset-4 rounded-full animate-pulse"
              style={{ background: 'linear-gradient(135deg, #8172AD, #4CAF50)', opacity: 0.4 }}
            />
            <div 
              className="absolute inset-8 rounded-full flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #8172AD, #4CAF50)' }}
            >
              <span className="text-white text-xs font-bold tracking-wider">Kailash</span>
            </div>
          </div>
        </div>
      )}
      
      {/* High-Quality Video Background */}
      <video
        ref={videoRef}
        className={`absolute inset-0 w-full h-full object-cover z-0 transition-opacity duration-1000 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
        style={{
          filter: 'brightness(0.95) contrast(1.05) saturate(1.1)',
          transform: 'scale(1.02)',
        }}
      >
        {/* High-quality 1080p HD video */}
        <source src="/kailash_video_hd.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      {/* Subtle animated gradient overlay for depth */}
      <div 
        className="absolute inset-0 z-[2] pointer-events-none opacity-30"
        style={{
          background: `
            radial-gradient(ellipse at 70% 30%, rgba(129, 114, 173, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 30% 70%, rgba(76, 175, 80, 0.1) 0%, transparent 50%)
          `,
          animation: 'pulse 8s ease-in-out infinite'
        }}
      />
    </>
  );
};

export default VideoBackground;
