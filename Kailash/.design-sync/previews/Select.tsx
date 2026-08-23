import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectGroup,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  Label,
} from 'frontend';

// SelectContent renders through a Radix portal only while the select is open;
// the closed trigger is the honest static state, so these cells show the trigger
// with and without a selected value.
export const WithValue = () => (
  <div className="w-[320px] space-y-2">
    <Label htmlFor="zone">Zone</Label>
    <Select defaultValue="gurugram">
      <SelectTrigger id="zone">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>North</SelectLabel>
          <SelectItem value="gurugram">Gurugram</SelectItem>
          <SelectItem value="cyber-city">Cyber City</SelectItem>
          <SelectItem value="sohna">Sohna Road</SelectItem>
        </SelectGroup>
        <SelectSeparator />
        <SelectGroup>
          <SelectLabel>West</SelectLabel>
          <SelectItem value="manesar">Manesar</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  </div>
);

export const Placeholder = () => (
  <div className="w-[320px] space-y-2">
    <Label htmlFor="conn">Connector type</Label>
    <Select>
      <SelectTrigger id="conn">
        <SelectValue placeholder="Choose a connector" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="ccs2">CCS2</SelectItem>
        <SelectItem value="type2">Type 2 AC</SelectItem>
        <SelectItem value="chademo">CHAdeMO</SelectItem>
      </SelectContent>
    </Select>
  </div>
);

export const Disabled = () => (
  <div className="w-[320px] space-y-2">
    <Label>Tariff plan</Label>
    <Select defaultValue="tod" disabled>
      <SelectTrigger>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="tod">Time-of-day</SelectItem>
      </SelectContent>
    </Select>
  </div>
);
