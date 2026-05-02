import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyA0dG3ApJUQ1QAqZ-Ok2IGkqp1xXrQQA5M",
  authDomain: "kailash-38268.firebaseapp.com",
  projectId: "kailash-38268",
  storageBucket: "kailash-38268.firebasestorage.app",
  messagingSenderId: "172604807567",
  appId: "1:172604807567:web:aea5f52ee0619cb8c113fa",
  measurementId: "G-M7HEJ3WJRM",
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
