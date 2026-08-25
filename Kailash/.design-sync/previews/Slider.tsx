import { Slider, Label } from 'frontend';

// NOTE ON THIS COMPONENT'S LIMITS — both discovered by grading, both real:
//  · `Slider` renders exactly ONE hardcoded <SliderPrimitive.Thumb />, so a
//    two-value range renders a filled segment with no upper handle. There is no
//    range story here because the component does not support one.
//  · Its only disabled styling is `disabled:opacity-50` on the thumb. Radix sets
//    `data-disabled`, not the `:disabled` pseudo-class, so that never fires and a
//    disabled slider is pixel-identical to an enabled one. No disabled story
//    either, for the same reason.
export const Default = () => (
  <div className="w-[420px] space-y-3">
    <div className="flex items-center justify-between">
      <Label>Output ceiling</Label>
      <span className="text-sm text-muted-foreground">60 kW</span>
    </div>
    <Slider defaultValue={[60]} max={120} step={5} />
  </div>
);

export const Positions = () => (
  <div className="w-[420px] space-y-6">
    <Slider defaultValue={[0]} max={100} />
    <Slider defaultValue={[35]} max={100} />
    <Slider defaultValue={[70]} max={100} />
    <Slider defaultValue={[100]} max={100} />
  </div>
);

export const PerZone = () => (
  <div className="w-[420px] space-y-5">
    {[
      ['Gurugram', 74],
      ['Cyber City', 41],
      ['Sohna Road', 96],
    ].map(([zone, v]) => (
      <div key={zone as string} className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>{zone}</Label>
          <span className="text-sm text-muted-foreground">{v}% of rated output</span>
        </div>
        <Slider defaultValue={[v as number]} max={100} />
      </div>
    ))}
  </div>
);
