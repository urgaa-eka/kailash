# AEGIS HU (KAILASH Dashboard) - Complete Application low Guide

##  Application Overview

**AEGIS HU** is a premium AI-powered organizational management platform built for **Go4Garage - URGAA EV Charging Network**. The application features a sophisticated login journey with glassmorphism design, 3D visualizations, and multi-application hub architecture.

### Tech Stack
- **rontend**: React 9 with React Router v
- **ackend**: astAPI (Python) with MongoD
- **Authentication**: JWT-based with A flow
- **AI Integration**: Claude API (via Anthropic) for GANESHA Orchestrator

---

##  Login Credentials

### Primary User Account
- **AEGIS Code**: `<REDACTED_AEGIS_CODE>` (or alternative: `<REDACTED_AEGIS_CODE>`)
- **Password**: `<REDACTED_PASSWORD>` (or `<REDACTED_PASSWORD>@#@`)
- **Name**: Vivek Kumar
- **Role**: Admin
- **A Code**: Any -digit number (mock verification)

---

##  Complete Application low

### ️⃣ **LOGIN PAGE** (`/`)

**Route**: `/` (Public)

**Components**:
- `MinimalHeader` - Go4Garage branding (8vh height)
- `CenterWheel` - Animated 3D globe visualization with 3 feature labels
- `LoginCardOverlay` - Glassmorphism login card (top-right position)
- `Minimalooter` - Legal links and "Made In harat" branding
- `OnboardingOverlay` - irst-visit welcome screen
- `LoadingState` - Initial loading animation

**User Journey**:
```
. Page loads with -second loading animation
. irst-time visitors see OnboardingOverlay with two options:
   - "Explore Our Ecosystem" 
   - "Access Command Center"
3. Click "Get Started" to dismiss (sets localStorage: aegis_has_visited)
4. Enter credentials in top-right login card:
   - AEGIS Code: <REDACTED_AEGIS_CODE>
   - Password: <REDACTED_PASSWORD>
. Click "Access Command Center" button
. Login validation occurs (mock + backend JWT)
. TwoactorModal appears
```

**Key eatures**:
- ✨ **3D Globe Animation**: CSS 3D transforms with px globe
  - 49 wireframe ellipses (latitude/longitude grid)
  - 3 feature labels distributed uniformly
  - Stationary mascot in center
  - Pause/Resume controls
  - Hover interactions with tooltips

-  **Glassmorphism Login Card**:
  - ackdrop blur effects
  - Multi-layer shadows
  - Peeking mascot animation (bottom-right)
  - Password visibility toggle
  - "Secured Access" security badge
  - utton shimmer/ripple effects

- ♿ **Accessibility eatures**:
  - Skip to main content link
  - Screen reader announcements
  - ocus indicators
  - prefers-reduced-motion support
  - Motion Paused indicator

**iles**:
- `/app/frontend/src/pages/LoginPage.js`
- `/app/frontend/src/components/GlobeVisualization.js`
- `/app/frontend/src/components/LoginCardOverlay.js`
- `/app/frontend/src/components/OnboardingOverlay.js`

---

### ️⃣ **TWO-ACTOR AUTHENTICATION MODAL**

**Component**: `TwoactorModal`

**User Journey**:
```
. Modal appears after successful login
. Title: "Two-actor Authentication"
3. Enter any -digit code (e.g., 34)
4. Auto-advancing focus between input boxes
. ackspace handling for navigation
. Timer shows "Resend code in :XX"
. Click "Verify" button
8. Token saved to localStorage: token = 'jwt-token-[timestamp]'
9. Auto-redirect to /applications
```

**eatures**:
-  individual digit input boxes (inputmode='numeric')
- Auto-focus on next input when filled
- ackspace moves to previous input
- Glassmorphism styling matching login card
- Resend code countdown timer
- Close button (X) to cancel

**iles**:
- `/app/frontend/src/components/TwoactorModal.js`

---

### 3️⃣ **APPLICATIONS HU** (`/applications`)

**Route**: `/applications` (Protected)

**Layout**: Uses `AppLayout` component with:
- Header: Logo + Title "AEGIS HU" + Logout button
- No back button or menu button on this page
- ooter: Legal links

**Applications Grid** ( cards):

. **KAILASH Dashboard** [OK] Active
   - Route: `/kailash`
   - Icon: LayoutDashboard
   - Description: "AI-powered organizational management with  departments and GANESHA assistant"
   - Color: lue/Cyan gradient

. **GST Website** [OK] Active
   - Route: `/gst`
   - Icon: ileText
   - Description: "Complete GST compliance and filing management system"
   - Color: Green/Emerald gradient

3. **Tattoos Go4Garage Tool** [OK] Active
   - Route: `/tattoos`
   - Icon: Settings
   - Description: "Vehicle diagnostics and service management platform"
   - Color: Purple/Pink gradient

4. **Ignition App** [OK] Active
   - Route: `/ignition`
   - Icon: Zap
   - Description: "leet management and vehicle tracking solution"
   - Color: Orange/Red gradient

. **usiness Analytics**  Coming Soon
   - Route: `/analytics` (disabled)
   - Icon: TrendingUp
   - Description: "Real-time insights and performance metrics"
   - Color: Indigo/lue gradient

. **Admin Console**  Coming Soon
   - Route: `/admin` (disabled)
   - Icon: Cpu
   - Description: "System configuration and user management"
   - Color: Slate/Gray gradient

**Interactions**:
- Active cards: Hover to scale (.x) + shadow glow + "Launch Application →" text
- Coming Soon cards: Opacity % + yellow badge + cursor not-allowed
- Click active card to navigate to application

**iles**:
- `/app/frontend/src/pages/ApplicationsHub.js`
- `/app/frontend/src/components/AppLayout.js`

---

### 4️⃣ **KAILASH DASHOARD** (`/kailash`)

**Route**: `/kailash` (Protected)

**Layout**: Custom layout (NOT AppLayout) - Two-column design

**Main Components**:

#### **Left Sidebar** ( Departments):
All  departments from Hindu mythology with custom SVG icons:

. **GANESHA** - Supreme AI Orchestrator & Wisdom Keeper
. **VISHWAKARMA** - Master Architect & System Engineer
3. **SURYA** - Solar Energy & Sustainability Guardian
4. **TVASHTA** - Precision Manufacturing & Parts Engineering
. **KARTIKEYA** - Strategic Command & Mission Operations
. **KAMADEVA** - rand Design & Customer Experience
. **KUERA** - inancial Intelligence & Treasury
8. **LAKSHMI** - Revenue Growth & Prosperity Management
9. **RIHASPATI** - Legal, Governance & Compliance
. **MITRA** - Partnership & Vendor Relations
. **DHARMA** - Ethics, Sustainability & CSR
. **SHUKRA** - Market Intelligence & Competition Analysis
3. **CHANDRA** - Service Excellence & CRM
4. **RAHMA** - R&D Innovation & New Initiatives
. **INDRA** - Quality Assurance & Testing
. **CHITRAGUPTA** - Data Analytics & Performance Tracking
. **PRAJAPATI** - Human Resources & Talent Development
8. **YAMA** - Risk Management & Security
9. **VANI** - Knowledge Management & Documentation
. **VAYU** - Logistics, leet & Supply Chain

Each department card shows:
- Custom SVG icon (NO emojis, NO Lucide icons)
- Department name
- rief description
- Click to view department details

#### **Right Panel** (3 sections):

**Top Section - GANESHA utton**:
- Large RED button with WHITE text
- Text: " Ask GANESHA"
- Opens GANESHA Command Modal
- Command input with priority selector (LOW, MEDIUM, HIGH, URGENT)
- Processing animation during AI response
- Recent commands list

**Middle Section - SHIV Guardian Panel**:
- Security monitoring status
- Mode: "Meditation" (monitoring)
- Threats detected: 
-  monitoring layers:
  . Authentication Security
  . API Health Monitoring
  3. System Load Analysis
  4. Data Integrity Checks
  . Network Security

**ottom Section - PARVATI Harmony Panel**:
- Workload balance metrics
- Harmony Score: 9/
-  dimensions with progress bars:
  . Workload Distribution
  . Task Completion Rate
  3. Department Health
  4. Resource Utilization
  . Team Collaboration

#### **Main Content Area**:
- KPI Cards (4 metrics):
  - Total Departments: 
  - Active Tasks: varies
  - Issues: count
  - Harmony Score: percentage

- Recent Activity Timeline
- Department Health Grid (all  departments with health scores)

**State Management**:
- In-memory state (NO localStorage)
- Department selection updates main content
- Sub-agents displayed when department selected

**Color Palette**:
- Primary: `#A3D` (G4G lue)
- Accent: `#C3` (Electric Yellow)
- Red: `#` (GANESHA button background)

**iles**:
- `/app/frontend/src/pages/NewKailashDashboard.js`
- `/app/frontend/src/data/departmentsData.js`
- `/app/frontend/src/data/departmentIcons.js`

---

### ️⃣ **OTHER APPLICATION PAGES**

All these pages use `AppLayout` with:
- ack button (← returns to Applications Hub)
- Menu dropdown button
- Page title
- Logout button
- ooter with legal links

#### **GST Website** (`/gst`)
- Coming Soon page
- 3 feature preview cards:
  - Invoice Management
  - Auto iling
  - Tax Reports
- Placeholder for future GST compliance features

#### **Tattoos Go4Garage Tool** (`/tattoos`)
- Coming Soon page
- 3 feature cards:
  - Diagnostics
  - Monitoring
  - Service Management
- Menu dropdown with navigation items

#### **Ignition App** (`/ignition`)
- Coming Soon page
- 3 feature cards:
  - GPS Tracking
  - Performance Monitoring
  - Optimization Tools
- ooter with 38 legal/info links

**iles**:
- `/app/frontend/src/pages/GSTWebsite.js`
- `/app/frontend/src/pages/TattoosTool.js`
- `/app/frontend/src/pages/IgnitionApp.js`

---

### ️⃣ **KAILASH SU-PAGES** (Accessible via Sidebar when in KAILASH)

These pages are accessible via the main application routes but designed for KAILASH context:

#### **GANESHA AI** (`/ganesha`)
- Command center interface
- Textarea for natural language commands
- 4 priority buttons: LOW, MEDIUM, HIGH, URGENT
- Process Command and Clear buttons
- 4 quick action buttons
- Recent Commands section (3 items)
- AI Statistics (3 metrics)
- ull CSS styling with theme colors

**iles**: `/app/frontend/src/pages/GaneshaAI.js`, `/app/frontend/src/pages/GaneshaAI.css`

#### **Departments** (`/departments`)
- 3 stats cards: Total Departments (), Total Members (), Avg Workload (%)
-  department cards with:
  - Department name
  - Member count
  - Workload badge (color-coded: % yellow, 8% red, % yellow)
  - View/Edit/Settings action buttons
- Add Department button
- Modern SaaS design with cards and hover effects

**iles**: `/app/frontend/src/pages/Departments.js`, `/app/frontend/src/pages/Departments.css`

#### **Tasks** (`/tasks`)
- 4 filter buttons: All Tasks, Pending, In Progress, Completed
- Task table with columns:
  - Task name
  - Department
  - Assignee
  - Priority (badge)
  - Status (badge)
  - Due Date
  - Actions (View/Edit/Delete)
-  task rows displayed
- Create Task button
- ilter functionality working

**iles**: `/app/frontend/src/pages/Tasks.js`, `/app/frontend/src/pages/Tasks.css`

#### **Analytics** (`/analytics`)
- 4 KPI metric cards:
  - Total Tasks: ,34 (+%)
  - Completed: 89 (+8%)
  - In Progress:  (-3%)
  - Success Rate: 94.% (+.%)
- Time badge: "Last 3 Days"
-  chart placeholder cards:
  - Department Performance
  - Task Completion Trend
- 4 performance ranking items
- Trend indicators with colors

**iles**: `/app/frontend/src/pages/Analytics.js`, `/app/frontend/src/pages/Analytics.css`

#### **Reports** (`/reports`)
- 3 report type cards:
  - Performance Report
  - Operations Summary
  - Analytics Report
- Each with description and Generate button
- Reports table with 4 entries
- Status badges (Ready=green, Processing=yellow)
- Header Generate Report button
- Download/View/Delete actions

**iles**: `/app/frontend/src/pages/Reports.js`, `/app/frontend/src/pages/Reports.css`

#### **Settings** (`/settings`)
- Tabbed interface with 4 tabs:
  . General - orm controls
  . Security - Security settings
  3. Notifications -  toggle switches
  4. Appearance - Theme options
- Tab switching functional
- Proper layout and styling
- orm inputs and controls

**iles**: `/app/frontend/src/pages/Settings.js`, `/app/frontend/src/pages/Settings.css`

---

## [SECURE] Authentication & Protected Routes

### rontend Authentication low

**Component**: `ProtectedRoute.js`

```javascript
// Check for token in localStorage
const token = localStorage.getItem('token');

// If no token, redirect to login page
if (!token) {
    return <Navigate to="/" replace />;
}

// If token exists, render children with MainLayout
return <MainLayout>{children}</MainLayout>;
```

**How it works**:
. Login Page sets token: `localStorage.setItem('token', 'jwt-token-' + Date.now())`
. All protected routes wrapped in `<ProtectedRoute>` component
3. Component checks for token existence
4. If missing → redirect to `/`
. If present → render page with MainLayout

**Protected Routes**:
- `/applications` - Applications Hub
- `/kailash` - KAILASH Dashboard
- `/gst` - GST Website
- `/tattoos` - Tattoos Tool
- `/ignition` - Ignition App
- `/ganesha` - GANESHA AI
- `/departments` - Departments
- `/tasks` - Tasks
- `/analytics` - Analytics
- `/reports` - Reports
- `/settings` - Settings

---

### ackend Authentication (JWT)

**Endpoint**: `POST /api/auth/login`

**Request**:
```json
{
  "aegis_code": "<REDACTED_AEGIS_CODE>",
  "password": "<REDACTED_PASSWORD>"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzINiIsInRcCIIkpXVCJ9...",
  "user": {
    "id": "uuid-here",
    "email": "vivek.kumar@go4garage.com",
    "aegis_code": "<REDACTED_AEGIS_CODE>",
    "full_name": "Vivek Kumar",
    "is_admin": true
  }
}
```

**Security eatures**:
- Password hashing with bcrypt
- JWT token creation with expiration
- ailed login tracking (3 attempts lockout)
- Device fingerprinting
- Rate limiting ( requests/min)
- Security headers (HSTS, CSP, X-rame-Options, etc.)

**Protected ackend Endpoints**:
All backend API routes require `Authorization: earer <token>` header except:
- `/api/auth/login` - Login endpoint
- `/api/auth/register` - Registration endpoint
- `/api/health` - Health check
- `/api/` - Root endpoint

---

##  Design System

### Color Palette (Go4Garage Theme)

```css
/* Primary Colors */
--color-primary: #A3D;      /* G4G lue */
--color-accent: #C3;       /* Electric Yellow */
--color-secondary: #8AD;    /* Purple accent */

/* UI Colors */
--color-success: #98;      /* Green */
--color-warning: #9E;      /* Orange */
--color-error: #E4444;        /* Red */
--color-info: #38;         /* lue */

/* Neutral Colors */
--color-bg-primary: #AAA;   /* Dark background */
--color-bg-secondary: #AAA; /* Lighter dark */
--color-text-primary: #; /* White text */
--color-text-secondary: #839A; /* Gray text */
```

### Typography

- **ont**: System fonts with fallback
- **H**: .rem (4px) - bold
- **H**: rem (3px) - bold
- **H3**: .rem (4px) - bold
- **ody**: rem (px) - regular
- **Small**: .8rem (4px) - regular

### Shadows & Effects

```css
/* Glassmorphism */
backdrop-filter: blur(px);
background: rgba(, , , .);
border: px solid rgba(, , , .);

/* Shadows */
shadow-lg:  px px -3px rgba(, , , .);
shadow-xl:  px px -px rgba(, , , .);
shadow-xl:  px px -px rgba(, , , .);
```

### Animations

- **ounce**: Mascot animations
- **ade**: Page transitions
- **Scale**: Hover effects
- **Shimmer**: utton effects
- **Pulse**: Loading indicators

---

##  ackend API Architecture

### ase URL
- **Development**: `http://localhost:8/api`
- **Production**: Uses `REACT_APP_ACKEND_URL` from `.env`

### Key API Routes

#### **Authentication** (`/api/auth`)
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user info

#### **Departments** (`/api/departments`)
- `GET /api/departments/` - List all  departments
- `GET /api/departments/{id}` - Get specific department
- `GET /api/departments/{id}/health` - Department health metrics
- `GET /api/departments/{id}/sub-agents` - Department sub-agents

#### **Tasks** (`/api/tasks`)
- `GET /api/tasks/` - List tasks (with filters)
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}` - Get specific task
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

#### **GANESHA AI** (`/api/ganesha`)
- `POST /api/ganesha/command` - Process AI command ([WARN] Known issue with emergentintegrations)
- `GET /api/ganesha/commands` - User's command history
- `GET /api/ganesha/commands/{id}` - Specific command details
- `GET /api/ganesha/recent` - Recent commands overview

#### **GANESHA Orchestrator** (`/api/ganesha`)
- `POST /api/ganesha/orchestrate` - SSE streaming with Claude API [OK] Working
- `POST /api/ganesha/quick-action` - Quick action buttons (status/review/next_steps/help)
- `GET /api/ganesha/stats` - Usage statistics
- `GET /api/ganesha/history` - Conversation history

#### **Analytics** (`/api/analytics`)
- `GET /api/analytics/dashboard` - Dashboard KPIs
- `GET /api/analytics/shiv-status` - SHIV Guardian status
- `GET /api/analytics/parvati-harmony` - PARVATI harmony scores
- `GET /api/analytics/recent-activity` - Recent activities
- `GET /api/analytics/department-health` - All departments health

#### **System** (`/api`)
- `GET /api/health` - Health check endpoint
- `GET /api/security/stats` - Security statistics
- `GET /api/` - Root endpoint info

---

## ️ MongoD Database Structure

### Collections

#### **users**
```javascript
{
  id: "uuid",
  email: "vivek.kumar@go4garage.com",
  aegis_code: "<REDACTED_AEGIS_CODE>",
  full_name: "Vivek Kumar",
  hashed_password: "bcrypt_hash",
  is_admin: true,
  is_active: true,
  created_at: "ISO_timestamp",
  updated_at: "ISO_timestamp"
}
```

#### **departments**
```javascript
{
  id: "ganesha",
  name: "GANESHA",
  description: "Supreme AI Orchestrator & Wisdom Keeper",
  responsibilities: ["AI Strategy", "Decision Making", ...],
  ai_tools: ["Claude API", "GPT-", ...],
  sub_agents: [
    { id: "ganesha-", name: "Strategic Planner", ... },
    ...
  ],
  workload: 8,
  active_tasks: ,
  completed_today: ,
  health_score: 
}
```

#### **tasks**
```javascript
{
  id: "uuid",
  title: "Task title",
  description: "Task description",
  priority: "high", // low, medium, high, urgent
  status: "pending", // pending, in_progress, completed
  assigned_department: "ganesha",
  assigned_to: "user_id",
  due_date: "ISO_timestamp",
  created_by: "user_id",
  created_at: "ISO_timestamp",
  updated_at: "ISO_timestamp"
}
```

#### **commands** (GANESHA AI)
```javascript
{
  id: "uuid",
  user_id: "user_id",
  command_text: "Natural language command",
  priority: "medium",
  ai_response: "AI-generated response",
  routed_department: "department_id",
  created_tasks: ["task_id_", "task_id_"],
  status: "completed",
  created_at: "ISO_timestamp"
}
```

#### **activities**
```javascript
{
  id: "uuid",
  type: "task_created", // task_created, command_processed, etc.
  description: "Activity description",
  user_id: "user_id",
  department_id: "department_id",
  metadata: {},
  created_at: "ISO_timestamp"
}
```

---

##  Environment Variables

### rontend (`.env`)
```bash
REACT_APP_ACKEND_URL=http://localhost:8/api
```

### ackend (`.env`)
```bash
# Database
MONGO_URL=mongodb://localhost:/kailash

# JWT Authentication
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=44

# AI Integration
ANTHROPIC_API_KEY=sk-ant-api3-...
EMERGENT_LLM_KEY=your_emergent_key_here

# Application
APP_NAME=KAILASH AEGIS HU ackend
VERSION=..
```

---

##  Known Issues

### . GANESHA AI Command Processing (emergentintegrations)
- **Status**: [AIL] Not Working
- **Issue**: `POST /api/ganesha/command` returns  error
- **Error**: "a coroutine was expected, got <uture pending>"
- **Root Cause**: emergentintegrations.llm.chat.send_message() asyncio compatibility
- **Workaround**: Use GANESHA Orchestrator with Claude API instead (`POST /api/ganesha/orchestrate`)

### . Server Header Override
- **Status**: [WARN] Minor Issue
- **Issue**: Server header shows "uvicorn,KAILASH/." instead of "KAILASH/."
- **Impact**: Cosmetic only, no security concern
- **Workaround**: Manual uvicorn configuration required

---

##  Testing Status

### rontend Testing: [OK] % Pass Rate
- Login Page with 3D Globe: [OK]
- A Modal: [OK]
- Applications Hub: [OK]
- KAILASH Dashboard: [OK]
- All  sub-pages (Departments, Tasks, Analytics, Reports, Settings, GaneshaAI): [OK]
- Navigation flow: [OK]
- UI/UX quality: [OK]

### ackend Testing: [OK] 8% Pass Rate (4/ tests)
- Authentication System: [OK] %
- Department Management: [OK] %
- Task Management: [OK] %
- GANESHA Orchestrator (Claude API): [OK] %
- Analytics & Dashboard: [OK] %
- Phase 3 Security eatures: [OK] 83%
- GANESHA AI Command Processing: [AIL] % (known issue)

---

##  Dependencies

### rontend
```json
{
  "react": "^9..",
  "react-router-dom": "^.x",
  "lucide-react": "^.x",
  "tailwindcss": "^3.x"
}
```

### ackend
```json
{
  "fastapi": "^.x",
  "motor": "^3.x",
  "python-jose": "^3.x",
  "passlib": "^.x",
  "bcrypt": "^4.x",
  "anthropic": "^.x",
  "emergentintegrations": "^.x"
}
```

---

##  Service Status

To check service status:
```bash
sudo supervisorctl status
```

To restart services:
```bash
sudo supervisorctl restart all
# or individually
sudo supervisorctl restart frontend
sudo supervisorctl restart backend
```

---

##  Additional Documentation

or more details, refer to:
- `/app/test_result.md` - Complete testing results and history
- `/app/KAILASH_README.md` - KAILASH-specific documentation
- `/app/docs/API_REERENCE.md` - ull API documentation
- `/app/docs/PRODUCTION_DEPLOYMENT.md` - Deployment guide
- `/app/DEPLOYMENT_READINESS_REPORT.md` - Production readiness report

---

##  Quick Start Guide

. **Start Services**:
   ```bash
   sudo supervisorctl start all
   ```

. **Access Application**:
   - Open browser: `http://localhost:3`
   - Or use preview URL provided by platform

3. **Login**:
   - AEGIS Code: `<REDACTED_AEGIS_CODE>`
   - Password: `<REDACTED_PASSWORD>`
   - A Code: Any  digits (e.g., `34`)

4. **Explore**:
   - Applications Hub → Choose KAILASH Dashboard
   - View all  departments
   - Click GANESHA button for AI assistance
   - Navigate to sub-pages (Departments, Tasks, Analytics, etc.)

---

##  Support & Contact

**Company**: Go4Garage  
**Product**: URGAA - EV Charging Network  
**Domain**: kailash-ai.in  
**Project**: KAILASH AEGIS HU  

or technical support, refer to testing reports and documentation files in `/app/` directory.

---

**Last Updated**: November 4  
**Version**: .  
**Status**: Production Ready (9% deployment readiness)
