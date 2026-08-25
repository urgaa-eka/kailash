import { EnhancedUserProfile } from 'frontend';

// Every prop has a default, so the zero-prop render is a real state; the other
// cells vary the deity avatar and the meditation indicator.
export const Default = () => <EnhancedUserProfile />;

export const CustomIdentity = () => (
  <EnhancedUserProfile
    name="Aarti Kulkarni"
    role="Head of Grid Operations"
    department="GRID OPS"
    deityId="vishwakarma"
  />
);

export const WithoutMeditation = () => (
  <EnhancedUserProfile
    name="Ravi Sharma"
    role="Field Maintenance Lead"
    department="FIELD"
    deityId="hanuman"
    showMeditation={false}
  />
);
