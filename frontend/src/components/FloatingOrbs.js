export const FloatingOrbs = () => {
  return (
    <>
      {/* Purple Orb - Top Left */}
      <div 
        className="absolute w-[300px] h-[300px] rounded-full blur-3xl opacity-20 pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(87, 6, 131, 0.6) 0%, transparent 70%)',
          top: '-100px',
          left: '-100px'
        }}
      />
      
      {/* Bright Green Orb - Bottom Right */}
      <div 
        className="absolute w-[250px] h-[250px] rounded-full blur-3xl opacity-20 pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(13, 163, 78, 0.6) 0%, transparent 70%)',
          bottom: '-80px',
          right: '-80px'
        }}
      />
    </>
  );
};

export default FloatingOrbs;