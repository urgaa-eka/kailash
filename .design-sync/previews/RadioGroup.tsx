import { RadioGroup, RadioGroupItem, Label } from 'frontend';

// RadioGroupItem reads the group's Radix context, so it is always composed
// inside <RadioGroup> here.
export const Default = () => (
  <RadioGroup defaultValue="tod" className="space-y-1">
    <div className="flex items-center space-x-2">
      <RadioGroupItem value="tod" id="r-tod" />
      <Label htmlFor="r-tod">Time-of-day</Label>
    </div>
    <div className="flex items-center space-x-2">
      <RadioGroupItem value="flat" id="r-flat" />
      <Label htmlFor="r-flat">Flat rate</Label>
    </div>
    <div className="flex items-center space-x-2">
      <RadioGroupItem value="dyn" id="r-dyn" />
      <Label htmlFor="r-dyn">Dynamic (grid-linked)</Label>
    </div>
  </RadioGroup>
);

export const WithDescriptions = () => (
  <RadioGroup defaultValue="all" className="w-[420px] space-y-3">
    {[
      ['all', 'Every fault', 'Page the on-call engineer for any fault code.'],
      ['repeat', 'Repeat faults only', 'Page only when the same code recurs within an hour.'],
      ['none', 'Digest', 'No paging; collect into the morning digest.'],
    ].map(([v, title, desc]) => (
      <div key={v} className="flex items-start space-x-3">
        <RadioGroupItem value={v} id={`rd-${v}`} className="mt-1" />
        <div className="space-y-0.5">
          <Label htmlFor={`rd-${v}`}>{title}</Label>
          <p className="text-sm text-muted-foreground">{desc}</p>
        </div>
      </div>
    ))}
  </RadioGroup>
);

export const Disabled = () => (
  <RadioGroup defaultValue="a" disabled className="space-y-1">
    <div className="flex items-center space-x-2">
      <RadioGroupItem value="a" id="rx-a" />
      <Label htmlFor="rx-a">Selected, disabled</Label>
    </div>
    <div className="flex items-center space-x-2">
      <RadioGroupItem value="b" id="rx-b" />
      <Label htmlFor="rx-b">Unselected, disabled</Label>
    </div>
  </RadioGroup>
);
