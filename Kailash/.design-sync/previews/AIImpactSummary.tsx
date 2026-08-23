import { AIImpactSummary } from 'frontend';

// AIImpactSummary carries its own defaults, so the zero-prop render is the real
// resting state; the second cell passes an explicit metrics object.
export const Default = () => <AIImpactSummary />;

export const WithMetrics = () => (
  <AIImpactSummary
    metrics={{
      problemsResolved: 128,
      fullyAutomated: 94,
      dataPoints: 41207,
      manualInterventions: 8,
      hoursSaved: 61,
    }}
  />
);
