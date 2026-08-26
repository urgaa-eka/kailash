export const MinimalFooter = () => {
  const currentYear = new Date().getFullYear();
  
  const links = [
    { label: "Terms & Conditions", href: "/terms", external: false },
    { label: "Privacy Policy", href: "/privacy", external: false },
    { label: "Compliance", href: "/compliance", external: false },
    { label: "OEMSG Registration", href: "/oemsg", external: false },
  ];

  return (
    <footer 
      className="min-h-[50px] flex items-center justify-center px-6 py-2" 
      style={{ 
        backgroundColor: '#ffffff'
      }}
      role="contentinfo"
    >
      <div className="flex flex-col items-center gap-2">
        {/* Main compliance links */}
        <div className="flex items-center gap-3 text-xs text-[hsl(var(--g4g-text-gray))]">
          {links.map((link, index) => (
            <div key={link.label} className="flex items-center gap-3">
              <a 
                href={link.href}
                target={link.external ? "_blank" : undefined}
                rel={link.external ? "noopener noreferrer" : undefined}
                className="hover:text-[hsl(var(--g4g-purple))] transition-colors focus:outline-2 focus:outline-[hsl(var(--g4g-bright-green))] focus:outline-offset-3 font-medium"
                tabIndex={0}
              >
                {link.label}
              </a>
              {index < links.length - 1 && (
                <span className="text-[hsl(var(--g4g-gray))]">|</span>
              )}
            </div>
          ))}
          <span className="text-[hsl(var(--g4g-gray))]">|</span>
          <span className="font-bold bg-gradient-to-r from-[hsl(var(--g4g-orange))] to-[hsl(var(--g4g-bright-green))] bg-clip-text text-transparent flex items-center gap-1">
            <span role="img" aria-label="India">🇮🇳</span>
            Made In Bharat
          </span>
        </div>
        
        {/* Copyright and additional info */}
        <div className="text-xs text-[hsl(var(--g4g-text-gray))] flex items-center gap-2">
          <span>© {currentYear} Go4Garage Pvt. Ltd. All rights reserved.</span>
          <span className="text-[hsl(var(--g4g-gray))]">|</span>
          <span>CIN: U74999DL2024PTC123456</span>
          <span className="text-[hsl(var(--g4g-gray))]">|</span>
          <span>ISO 27001:2013 Certified</span>
        </div>
      </div>
    </footer>
  );
};

export default MinimalFooter;