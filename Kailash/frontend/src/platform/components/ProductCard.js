import { ChevronRight } from "lucide-react";

export const ProductCard = ({ icon: Icon, name, description, gradient }) => {
  return (
    <div className="group bg-white rounded-lg p-3 border-l-4 hover:-translate-y-1 transition-all duration-300 cursor-pointer" style={{ borderImage: gradient ? `linear-gradient(to bottom, ${gradient.replace('from-', '').replace('via-', ', ').replace('to-', ', ')}) 1` : 'none', borderLeft: '4px solid', borderImageSlice: 1, boxShadow: '0 2px 8px rgba(87, 6, 131, 0.08)' }}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <div className={`w-8 h-8 rounded-lg ${gradient ? `bg-gradient-to-br ${gradient}` : 'bg-[hsl(var(--g4g-purple))]'} flex items-center justify-center`}>
            <Icon className="w-5 h-5 text-white" strokeWidth={1.5} />
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm text-[hsl(var(--g4g-purple))] mb-0.5">{name}</h3>
          <p className="text-xs text-[hsl(var(--g4g-text-gray))] leading-relaxed line-clamp-1">{description}</p>
        </div>
        <ChevronRight className="flex-shrink-0 w-4 h-4 text-[hsl(var(--g4g-purple))] opacity-0 group-hover:opacity-100 transition-opacity" strokeWidth={1.5} />
      </div>
    </div>
  );
};

export default ProductCard;