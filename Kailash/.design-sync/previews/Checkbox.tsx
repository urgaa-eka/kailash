import { Checkbox, Label } from 'frontend';

export const States = () => (
  <div className="space-y-3">
    <div className="flex items-center space-x-2">
      <Checkbox id="c-on" defaultChecked />
      <Label htmlFor="c-on">Checked</Label>
    </div>
    <div className="flex items-center space-x-2">
      <Checkbox id="c-off" />
      <Label htmlFor="c-off">Unchecked</Label>
    </div>
    <div className="flex items-center space-x-2">
      <Checkbox id="c-dis" disabled />
      <Label htmlFor="c-dis">Disabled</Label>
    </div>
    <div className="flex items-center space-x-2">
      <Checkbox id="c-dis-on" defaultChecked disabled />
      <Label htmlFor="c-dis-on">Disabled, checked</Label>
    </div>
  </div>
);

export const OptionList = () => (
  <div className="w-[380px] space-y-3">
    <p className="text-sm font-semibold">Notify on</p>
    {[
      ['Connector faults', true],
      ['Transformer derating', true],
      ['Settlement mismatches', false],
      ['Firmware rollouts', false],
    ].map(([label, on]) => (
      <div key={label as string} className="flex items-center space-x-2">
        <Checkbox id={label as string} defaultChecked={on as boolean} />
        <Label htmlFor={label as string} className="font-normal">
          {label}
        </Label>
      </div>
    ))}
  </div>
);

export const WithDescription = () => (
  <div className="flex w-[420px] items-start space-x-3">
    <Checkbox id="ack" defaultChecked className="mt-0.5" />
    <div className="space-y-1">
      <Label htmlFor="ack">Acknowledge the lockout</Label>
      <p className="text-sm text-muted-foreground">
        The connector stays unavailable until a field engineer clears it on site.
      </p>
    </div>
  </div>
);
