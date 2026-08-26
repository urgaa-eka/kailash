export const LoginFooter = () => {
  const links = [
    { label: "Terms & Conditions", href: "#" },
    { label: "Privacy Policy", href: "#" },
    { label: "Compliance", href: "#" },
    { label: "OEMSG Registration", href: "#" },
  ];

  return (
    <footer className="h-12 bg-[hsl(var(--g4g-light-gray))] border-t border-[hsl(var(--g4g-gray))] flex items-center justify-center px-6">
      <div className="flex items-center gap-3 text-xs text-[hsl(var(--g4g-text-gray))]">
        {links.map((link, index) => (
          <div key={link.label} className="flex items-center gap-3">
            <a 
              href={link.href}
              className="hover:text-[hsl(var(--g4g-purple))] transition-colors"
            >
              {link.label}
            </a>
            {index < links.length - 1 && (
              <span className="text-[hsl(var(--g4g-gray))]">|</span>
            )}
          </div>
        ))}
        
        <span className="text-[hsl(var(--g4g-gray))]">|</span>
        
        <span className="font-bold text-[hsl(var(--g4g-orange))] flex items-center gap-1">
          <span>🇮🇳</span>
          Made In Bharat
        </span>
      </div>
    </footer>
  );
};

export default LoginFooter;