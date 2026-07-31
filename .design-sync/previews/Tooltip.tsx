import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  Button,
  Zap,
} from 'frontend';
// `open` is forced — tooltips only appear on hover/focus. TooltipProvider comes
// from DesignSystemProvider, which wraps every preview.
export const Open = () => (
  <Tooltip open>
    <TooltipTrigger asChild>
      <Button variant="outline" size="icon" aria-label="Provision charger">
        <Zap />
      </Button>
    </TooltipTrigger>
    <TooltipContent side="right">Provision a new charger at this station</TooltipContent>
  </Tooltip>
);
