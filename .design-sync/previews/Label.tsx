import { Label, Input, Checkbox, Textarea } from 'frontend';

export const WithInput = () => (
  <div className="w-[380px] space-y-2">
    <Label htmlFor="tariff">Tariff plan</Label>
    <Input id="tariff" defaultValue="Time-of-day · Zone A" />
  </div>
);

export const WithCheckbox = () => (
  <div className="flex items-center space-x-2">
    <Checkbox id="notify" defaultChecked />
    <Label htmlFor="notify">Notify Field Maintenance on repeat faults</Label>
  </div>
);

export const WithTextarea = () => (
  <div className="w-[380px] space-y-2">
    <Label htmlFor="note">Dispatch note</Label>
    <Textarea id="note" defaultValue="Connector 3 locked out pending inspection." />
  </div>
);

// peer-disabled:* in the base class only fires when the label is a sibling of a
// disabled peer, which is what this cell sets up.
export const DisabledPeer = () => (
  <div className="w-[380px] space-y-2">
    <Input id="ro" className="peer" defaultValue="Read-only field" disabled />
    <Label htmlFor="ro">Locked while the session is active</Label>
  </div>
);
