import { Avatar, AvatarImage, AvatarFallback } from 'frontend';

export const Fallbacks = () => (
  <div className="flex items-center gap-4">
    <Avatar>
      <AvatarFallback>AK</AvatarFallback>
    </Avatar>
    <Avatar>
      <AvatarFallback>RS</AvatarFallback>
    </Avatar>
    <Avatar>
      <AvatarFallback className="bg-[hsl(var(--g4g-purple))] text-white">GO</AvatarFallback>
    </Avatar>
    <Avatar>
      <AvatarFallback className="bg-[hsl(var(--g4g-green))] text-white">FM</AvatarFallback>
    </Avatar>
  </div>
);

export const Sizes = () => (
  <div className="flex items-end gap-4">
    <Avatar className="h-8 w-8">
      <AvatarFallback className="text-xs">SM</AvatarFallback>
    </Avatar>
    <Avatar>
      <AvatarFallback>MD</AvatarFallback>
    </Avatar>
    <Avatar className="h-14 w-14">
      <AvatarFallback className="text-lg">LG</AvatarFallback>
    </Avatar>
  </div>
);

// AvatarImage renders when the source loads and yields to AvatarFallback when it
// does not — which is what this cell shows, since preview capture runs offline.
export const WithImage = () => (
  <div className="flex items-center gap-4">
    <Avatar>
      <AvatarImage src="/avatars/grid-ops.png" alt="Grid Operations lead" />
      <AvatarFallback>GO</AvatarFallback>
    </Avatar>
    <Avatar>
      <AvatarImage src="/avatars/care.png" alt="Customer Care lead" />
      <AvatarFallback>CC</AvatarFallback>
    </Avatar>
  </div>
);

// Overlap is kept to a quarter of the avatar width: at -space-x-3 on the
// default 40px avatar the next avatar covers the previous one's initials.
export const Stack = () => (
  <div className="flex -space-x-1.5">
    <Avatar className="h-12 w-12 ring-[3px] ring-white">
      <AvatarFallback className="bg-[hsl(var(--g4g-purple))] text-white">AK</AvatarFallback>
    </Avatar>
    <Avatar className="h-12 w-12 ring-[3px] ring-white">
      <AvatarFallback className="bg-[hsl(var(--g4g-green))] text-white">RS</AvatarFallback>
    </Avatar>
    <Avatar className="h-12 w-12 ring-[3px] ring-white">
      <AvatarFallback className="bg-[hsl(var(--g4g-purple-light))] text-white">MP</AvatarFallback>
    </Avatar>
    <Avatar className="h-12 w-12 ring-[3px] ring-white">
      <AvatarFallback className="text-xs">+9</AvatarFallback>
    </Avatar>
  </div>
);
