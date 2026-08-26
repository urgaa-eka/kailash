import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import { ToastProvider } from "./context/ToastContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
// ApplicationsHub REMOVED - KAILASH IS the operating system
import SpiritualKailashDashboard from "./pages/SpiritualKailashDashboard";
import GSTWebsite from "./pages/GSTWebsite";
import TattoosTool from "./pages/TattoosTool";
import IgnitionApp from "./pages/IgnitionApp";

// New Pages
import GaneshaAI from "./pages/GaneshaAI";
import Departments from "./pages/Departments";
import Tasks from "./pages/Tasks";
import Analytics from "./pages/Analytics";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";

// V2 Feature Pages
import Chat from "./pages/Chat";
import Users from "./pages/Users";
import Urjaa from "./pages/Urjaa";
import Guardians from "./pages/Guardians";
import AutomobilePricing from "./pages/AutomobilePricing";

// V3 Feature Pages - Investor Demo
import InvestorExecutiveDashboard from "./pages/InvestorExecutiveDashboard";
import DepartmentDetailNew from "./pages/DepartmentDetailNew";
import GaneshaChatV2 from "./pages/GaneshaChatV2";
import GapsTasksManagement from "./pages/GapsTasksManagement";
import KnowledgeBase from "./pages/KnowledgeBase";
import GaneshaAnalytics from "./pages/GaneshaAnalytics";
import Go4GarageFinancials from "@/features/company/Go4GarageFinancials";

// Import theme
import "./styles/theme.css";
import "./styles/spiritual-theme.css";

// Legal Pages - Group 1: General Legal
import TermsAndConditions from "@/features/legal/TermsAndConditions";
import PrivacyPolicy from "@/features/legal/PrivacyPolicy";
import CookiePolicy from "@/features/legal/CookiePolicy";
import DisclaimerPolicy from "@/features/legal/DisclaimerPolicy";
import AcceptableUsePolicy from "@/features/legal/AcceptableUsePolicy";
import IntellectualProperty from "@/features/legal/IntellectualProperty";
import DMCAPolicy from "@/features/legal/DMCAPolicy";
import AgeRestrictionPolicy from "@/features/legal/AgeRestrictionPolicy";

// Legal Pages - Group 2: Data & Privacy
import GDPRCompliance from "@/features/legal/GDPRCompliance";
import CCPACompliance from "@/features/legal/CCPACompliance";
import DataRetentionPolicy from "@/features/legal/DataRetentionPolicy";
import DataBreachPolicy from "@/features/legal/DataBreachPolicy";
import DataTransferPolicy from "@/features/legal/DataTransferPolicy";
import SubprocessorList from "@/features/legal/SubprocessorList";
import UserRights from "@/features/legal/UserRights";

// Legal Pages - Group 3: Services & Operations
import SLA from "@/features/legal/SLA";
import RefundPolicy from "@/features/legal/RefundPolicy";
import ShippingPolicy from "@/features/legal/ShippingPolicy";
import WarrantyPolicy from "@/features/legal/WarrantyPolicy";
import APITerms from "@/features/legal/APITerms";
import OEMSGRegistration from "@/features/legal/OEMSGRegistration";

// Legal Pages - Group 4: Community & Guidelines
import CommunityGuidelines from "@/features/legal/CommunityGuidelines";
import ModeratorGuidelines from "@/features/legal/ModeratorGuidelines";
import CodeOfConduct from "@/features/legal/CodeOfConduct";
import Ethics from "@/features/legal/Ethics";

// Legal Pages - Group 5: Security & Compliance
import SecurityPolicy from "@/features/legal/SecurityPolicy";
import IncidentResponse from "@/features/legal/IncidentResponse";
import PenTest from "@/features/legal/PenTest";
import BugBounty from "@/features/legal/BugBounty";
import AccessibilityStatement from "@/features/legal/AccessibilityStatement";
import Compliance from "@/features/legal/Compliance";

// Legal Pages - Group 6: About & Transparency
import Transparency from "@/features/legal/Transparency";

// Components
import LegalFooter from "./components/LegalFooter";
import CookieConsent from "./components/CookieConsent";
import ErrorBoundary from "./components/ErrorBoundary";
import SessionTimeout from "./components/SessionTimeout";
import { Toaster } from "./components/UI/sonner";
import "./App.css";

// Check if user is authenticated
const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

// Layout wrapper to conditionally show footer
function Layout({ children }) {
  const location = useLocation();
  const hideFooterPaths = ["/", "/kailash", "/dashboard/executive", "/ganesha-v2"];
  const showFooter = !hideFooterPaths.includes(location.pathname) && !location.pathname.startsWith('/department/');
  const authenticated = isAuthenticated();

  return (
    <>
      {children}
      {showFooter && <LegalFooter />}
      <CookieConsent />
      <SessionTimeout isAuthenticated={authenticated} />
    </>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <div className="App">
        <BrowserRouter>
          <ToastProvider>
            <Layout>
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<LoginPage />} />
              
              {/* Redirect /dashboard to /kailash - KAILASH Command is primary landing */}
              <Route path="/dashboard" element={<Navigate to="/kailash" replace />} />
              
              {/* Redirect /applications to /dashboard - KAILASH IS the OS */}
              <Route path="/applications" element={<Navigate to="/dashboard" replace />} />
              
              <Route path="/kailash" element={
                <ProtectedRoute noLayout={true}>
                  <SpiritualKailashDashboard />
                </ProtectedRoute>
              } />
              
              {/* Application routes with proper pages */}
            <Route path="/gst" element={
              <ProtectedRoute>
                <GSTWebsite />
              </ProtectedRoute>
            } />
            <Route path="/tattoos" element={
              <ProtectedRoute>
                <TattoosTool />
              </ProtectedRoute>
            } />
            <Route path="/ignition" element={
              <ProtectedRoute>
                <IgnitionApp />
              </ProtectedRoute>
            } />
            
            {/* New Application Pages */}
            <Route path="/ganesha" element={
              <ProtectedRoute>
                <GaneshaAI />
              </ProtectedRoute>
            } />
            <Route path="/departments" element={
              <ProtectedRoute>
                <Departments />
              </ProtectedRoute>
            } />
            <Route path="/tasks" element={
              <ProtectedRoute>
                <Tasks />
              </ProtectedRoute>
            } />
            <Route path="/analytics" element={
              <ProtectedRoute>
                <Analytics />
              </ProtectedRoute>
            } />
            <Route path="/reports" element={
              <ProtectedRoute>
                <Reports />
              </ProtectedRoute>
            } />
            <Route path="/settings" element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } />
            
            {/* V2 Feature Routes */}
            <Route path="/chat" element={
              <ProtectedRoute noLayout={true}>
                <Chat />
              </ProtectedRoute>
            } />
            <Route path="/users" element={
              <ProtectedRoute>
                <Users />
              </ProtectedRoute>
            } />
            <Route path="/urjaa" element={
              <ProtectedRoute>
                <Urjaa />
              </ProtectedRoute>
            } />
            <Route path="/guardians" element={
              <ProtectedRoute>
                <Guardians />
              </ProtectedRoute>
            } />
            <Route path="/automobile" element={
              <ProtectedRoute>
                <AutomobilePricing />
              </ProtectedRoute>
            } />

            {/* V3 Investor Demo Routes */}
            <Route path="/dashboard/executive" element={
              <ProtectedRoute noLayout={true}>
                <InvestorExecutiveDashboard />
              </ProtectedRoute>
            } />
            <Route path="/department/:name" element={
              <ProtectedRoute noLayout={true}>
                <DepartmentDetailNew />
              </ProtectedRoute>
            } />
            <Route path="/ganesha-v2" element={
              <ProtectedRoute noLayout={true}>
                <GaneshaChatV2 />
              </ProtectedRoute>
            } />
            <Route path="/management" element={
              <ProtectedRoute noLayout={true}>
                <GapsTasksManagement />
              </ProtectedRoute>
            } />
            <Route path="/knowledge-base" element={
              <ProtectedRoute noLayout={true}>
                <KnowledgeBase />
              </ProtectedRoute>
            } />
            <Route path="/ganesha-analytics" element={
              <ProtectedRoute noLayout={true}>
                <GaneshaAnalytics />
              </ProtectedRoute>
            } />

            {/* Go4Garage Financial Controller — serverless FY dashboard.
                Self-gates with Supabase Auth (see Go4GarageFinancials), so it
                does NOT use the app's Firebase ProtectedRoute: it runs on
                Firebase Hosting + Supabase with no application backend. */}
            <Route path="/financials" element={<Go4GarageFinancials />} />
            <Route path="/dashboard/financials" element={<Go4GarageFinancials />} />

            {/* Legal Routes - Group 1: General Legal */}
            <Route path="/terms" element={<TermsAndConditions />} />
            <Route path="/privacy" element={<PrivacyPolicy />} />
            <Route path="/cookie-policy" element={<CookiePolicy />} />
            <Route path="/disclaimer" element={<DisclaimerPolicy />} />
            <Route path="/acceptable-use" element={<AcceptableUsePolicy />} />
            <Route path="/intellectual-property" element={<IntellectualProperty />} />
            <Route path="/dmca" element={<DMCAPolicy />} />
            <Route path="/age-restriction" element={<AgeRestrictionPolicy />} />

            {/* Legal Routes - Group 2: Data & Privacy */}
            <Route path="/gdpr-compliance" element={<GDPRCompliance />} />
            <Route path="/ccpa-compliance" element={<CCPACompliance />} />
            <Route path="/data-retention" element={<DataRetentionPolicy />} />
            <Route path="/data-breach" element={<DataBreachPolicy />} />
            <Route path="/data-transfer" element={<DataTransferPolicy />} />
            <Route path="/subprocessors" element={<SubprocessorList />} />
            <Route path="/user-rights" element={<UserRights />} />

            {/* Legal Routes - Group 3: Services & Operations */}
            <Route path="/sla" element={<SLA />} />
            <Route path="/refund-policy" element={<RefundPolicy />} />
            <Route path="/shipping-policy" element={<ShippingPolicy />} />
            <Route path="/warranty-policy" element={<WarrantyPolicy />} />
            <Route path="/api-terms" element={<APITerms />} />
            <Route path="/oemsg" element={<OEMSGRegistration />} />

            {/* Legal Routes - Group 4: Community & Guidelines */}
            <Route path="/community-guidelines" element={<CommunityGuidelines />} />
            <Route path="/moderator-guidelines" element={<ModeratorGuidelines />} />
            <Route path="/code-of-conduct" element={<CodeOfConduct />} />
            <Route path="/ethics" element={<Ethics />} />

            {/* Legal Routes - Group 5: Security & Compliance */}
            <Route path="/security-policy" element={<SecurityPolicy />} />
            <Route path="/incident-response" element={<IncidentResponse />} />
            <Route path="/penetration-testing" element={<PenTest />} />
            <Route path="/bug-bounty" element={<BugBounty />} />
            <Route path="/accessibility" element={<AccessibilityStatement />} />
            <Route path="/compliance" element={<Compliance />} />

            {/* Legal Routes - Group 6: About & Transparency */}
            <Route path="/transparency" element={<Transparency />} />
          </Routes>
        </Layout>
        </ToastProvider>
      </BrowserRouter>
      <Toaster />
    </div>
    </ErrorBoundary>
  );
}

export default App;