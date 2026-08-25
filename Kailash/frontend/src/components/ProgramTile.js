import { Badge } from "./UI/badge";

export const ProgramTile = ({ icon: Icon, name, badge, description }) => {
  return (
    <div className="group rounded-xl p-4 border hover:-translate-y-1 hover:shadow-lg transition-all duration-300 cursor-pointer" style={{ background: 'linear-gradient(90deg, rgba(87, 6, 131, 0.05), transparent)', borderColor: 'rgba(87, 6, 131, 0.1)' }}>
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style={{ background: 'linear-gradient(135deg, hsl(var(--g4g-purple)), hsl(var(--g4g-purple) / 0.7))' }}>
          <Icon className="w-5 h-5 text-white" strokeWidth={1.5} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-sm text-[hsl(var(--g4g-purple))]">{name}</h3>
            <Badge variant="secondary" className="text-xs px-2 py-0 h-5" style={{ backgroundColor: 'rgba(87, 6, 131, 0.05)', color: 'hsl(var(--g4g-purple))', border: '1px solid rgba(87, 6, 131, 0.2)' }}>
              {badge}
            </Badge>
          </div>
          <p className="text-xs text-[hsl(var(--g4g-text-gray))] line-clamp-1">{description}</p>
        </div>
      </div>
    </div>
  );
};

export default ProgramTile;