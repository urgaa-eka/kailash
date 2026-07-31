import { LoadingState } from 'frontend';

// LoadingState takes no props and fills the viewport (h-screen w-screen); the
// card override gives it a viewport to fill. Its mascot is fetched from a remote
// asset host, so in an offline capture only the wordmark and the pulse dots
// render — which is also what a user on a slow link sees first.
export const Default = () => <LoadingState />;
