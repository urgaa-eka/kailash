import { Badge, Zap } from 'frontend';
export const Variants = () => (
  <div className="flex flex-wrap items-center gap-2">
    <Badge>Active</Badge>
    <Badge variant="secondary">Scheduled</Badge>
    <Badge variant="outline">Idle</Badge>
    <Badge variant="destructive">Faulted</Badge>
  </div>
);

export const InContext = () => (
  <div className="flex flex-wrap items-center gap-2">
    <Badge>
      <Zap className="mr-1 h-3 w-3" />
      Fast charging
    </Badge>
    <Badge variant="secondary">OCPI 2.2</Badge>
    <Badge variant="outline">CCS2</Badge>
    <Badge variant="outline">Type 2 AC</Badge>
  </div>
);

export const Counts = () => (
  <div className="flex flex-wrap items-center gap-2">
    <Badge variant="secondary">14 open</Badge>
    <Badge variant="destructive">3 breached</Badge>
    <Badge variant="outline">128 resolved</Badge>
  </div>
);
