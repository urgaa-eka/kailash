export const ServiceRow = ({ icon: Icon, name, description }) => {
  return (
    <div className="group py-3 border-b hover:bg-[rgba(87,6,131,0.02)] transition-all duration-300 cursor-pointer" style={{ borderColor: 'rgba(87, 6, 131, 0.08)' }}>
      <div className="flex items-center gap-4">
        <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-[hsl(var(--g4g-purple))] to-[hsl(var(--g4g-bright-green))] flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
          <Icon className="w-6 h-6 text-white" strokeWidth={1.5} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm text-[hsl(var(--g4g-purple))] mb-0.5">{name}</h3>
          <p className="text-xs text-[hsl(var(--g4g-text-gray))] line-clamp-1">{description}</p>
        </div>
      </div>
      <div className="mt-2 h-0.5 w-full bg-gradient-to-r from-[hsl(var(--g4g-purple))] via-[hsl(var(--g4g-green))] to-transparent opacity-20 group-hover:opacity-40 transition-opacity" />
    </div>
  );
};

export default ServiceRow;