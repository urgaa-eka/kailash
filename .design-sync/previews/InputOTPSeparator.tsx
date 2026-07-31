import { InputOTP, InputOTPGroup, InputOTPSlot, InputOTPSeparator, Label } from 'frontend';

// InputOTPSeparator is a bare dash glyph; it only reads as a separator between
// two InputOTPGroups, so both cells compose it there.
export const BetweenGroups = () => (
  <div className="space-y-2">
    <Label>Two-factor code</Label>
    <InputOTP maxLength={6} value="428913">
      <InputOTPGroup>
        <InputOTPSlot index={0} />
        <InputOTPSlot index={1} />
        <InputOTPSlot index={2} />
      </InputOTPGroup>
      <InputOTPSeparator />
      <InputOTPGroup>
        <InputOTPSlot index={3} />
        <InputOTPSlot index={4} />
        <InputOTPSlot index={5} />
      </InputOTPGroup>
    </InputOTP>
  </div>
);

export const ThreePairs = () => (
  <div className="space-y-2">
    <Label>Station pairing code</Label>
    <InputOTP maxLength={6} value="931744">
      <InputOTPGroup>
        <InputOTPSlot index={0} />
        <InputOTPSlot index={1} />
      </InputOTPGroup>
      <InputOTPSeparator />
      <InputOTPGroup>
        <InputOTPSlot index={2} />
        <InputOTPSlot index={3} />
      </InputOTPGroup>
      <InputOTPSeparator />
      <InputOTPGroup>
        <InputOTPSlot index={4} />
        <InputOTPSlot index={5} />
      </InputOTPGroup>
    </InputOTP>
  </div>
);
