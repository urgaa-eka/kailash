import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";

// kailash-29111, web app "kailash-ai" — the project kailash-ai.com resolves to.
// Values are the authoritative ones from `firebase apps:sdkconfig WEB`, not a
// projectId swap: apiKey, appId, messagingSenderId and measurementId are all
// per-project and would silently point analytics at the wrong place otherwise.
const firebaseConfig = {
  // Firebase web API keys ship in every client bundle. Access is controlled by
  // referrer restrictions and security rules, not by keeping this string secret.
  // secret-scan: allow public by design, shipped in the client bundle
  apiKey: "AIzaSyDD70yOW6vheOK2OPzNXT0b0R5B9ZXI1ho",
  authDomain: "kailash-29111.firebaseapp.com",
  projectId: "kailash-29111",
  storageBucket: "kailash-29111.firebasestorage.app",
  messagingSenderId: "794735482892",
  appId: "1:794735482892:web:b43c18163d5d9dd024b629",
  measurementId: "G-H5D59BZN6F",
};

const app = initializeApp(firebaseConfig);

// Analytics — only in browser environments that support it
let analytics = null;
isSupported().then((supported) => {
  if (supported) {
    analytics = getAnalytics(app);
  }
});

export { app, analytics };
export default app;
