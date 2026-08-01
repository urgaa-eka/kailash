import { HoverCard, HoverCardTrigger, HoverCardContent, Avatar, AvatarFallback, Button } from 'frontend';

// `open` is forced: the content only appears on pointer hover, which a static
// capture cannot produce.
export const Open = () => (
  <HoverCard open>
    <HoverCardTrigger asChild>
      <Button variant="link" className="px-0">
        Urjaa North Hub
      </Button>
    </HoverCardTrigger>
    <HoverCardContent className="w-80">
      <div className="flex gap-3">
        <Avatar>
          <AvatarFallback className="bg-[hsl(var(--g4g-purple))] text-white">UH</AvatarFallback>
        </Avatar>
        <div className="space-y-1">
          <h4 className="text-sm font-semibold">Urjaa North Hub</h4>
          <p className="text-sm text-muted-foreground">
            12 DC fast chargers · Gurugram · commissioned March 2025
          </p>
          <p className="text-xs text-muted-foreground">99.1% uptime over 30 days</p>
        </div>
      </div>
    </HoverCardContent>
  </HoverCard>
);
