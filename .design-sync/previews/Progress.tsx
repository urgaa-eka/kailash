import { Progress } from 'frontend';

export const Levels = () => (
  <div className="w-[420px] space-y-5">
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span>Grid load</span>
        <span className="text-muted-foreground">18%</span>
      </div>
      <Progress value={18} />
    </div>
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span>Evening window</span>
        <span className="text-muted-foreground">62%</span>
      </div>
      <Progress value={62} />
    </div>
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span>Transformer capacity</span>
        <span className="text-muted-foreground">91%</span>
      </div>
      <Progress value={91} />
    </div>
  </div>
);

export const Boundaries = () => (
  <div className="w-[420px] space-y-5">
    <Progress value={0} />
    <Progress value={50} />
    <Progress value={100} />
  </div>
);

export const Inline = () => (
  <div className="w-[420px] space-y-3">
    {[
      ['Gurugram', 74],
      ['Cyber City', 41],
      ['Sohna Road', 96],
    ].map(([zone, v]) => (
      <div key={zone as string} className="flex items-center gap-3">
        <span className="w-28 shrink-0 text-sm">{zone}</span>
        <Progress value={v as number} className="h-2" />
        <span className="w-10 shrink-0 text-right text-xs text-muted-foreground">{v}%</span>
      </div>
    ))}
  </div>
);
