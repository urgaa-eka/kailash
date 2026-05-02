# KAILASH-AI KNOWLEDGE TRAINING ARCHITECTURE

## 🎯 Overview

The KAILASH-AI Knowledge Training Architecture is a revolutionary two-layer system that provides each AI department with deep domain expertise and real-time market intelligence.

---

## 📊 Architecture Layers

### Layer 1: PRE-DATA (Foundation)
**Static knowledge files providing foundational expertise**

- **Location**: `/app/backend/knowledge/pre-data/`
- **Structure**:
  - `global/` - System-wide knowledge
  - `internal/` - 15 internal departments
  - `external/` - 5 external departments

- **Content per Department** (4 files):
  1. `domain_expertise.md` - Core competencies and areas of expertise
  2. `rules.json` - Operational rules and configurations
  3. `policies.md` - Governance policies and standards
  4. `sop.md` - Standard operating procedures

- **Total Files**: 84 knowledge files (4 files × 21 departments)

### Layer 2: POST-DATA (Continuous Learning)
**Daily intelligence gathering via Perplexity API**

- **Location**: `/app/backend/knowledge/post-data/`
- **Schedule**: Daily at 06:00 UTC (configurable)
- **Process**:
  1. Query Perplexity API for latest market intelligence
  2. Process with Claude LLM for relevance extraction
  3. Store dated intelligence per department
  4. Generate daily digest summary

- **Storage Structure**:
  ```
  post-data/
  ├── daily-digest/
  │   └── 2025-12-15/
  │       ├── summary.json
  │       ├── lakshmi.json
  │       ├── vishwakarma.json
  │       └── ... (20 department files)
  └── department-specific/
      ├── internal/
      │   ├── lakshmi/
      │   │   └── 2025-12-15.json
      │   └── ...
      └── external/
          ├── surya/
          │   └── 2025-12-15.json
          └── ...
  ```

---

## 🏢 Departments Covered

### Internal Departments (15)
1. **LAKSHMI** - Financial Management & Prosperity
2. **VISHWAKARMA** - Technical Innovation & Engineering
3. **AGNI** - Energy & Infrastructure
4. **INDRA** - Security & Protection
5. **VAYU** - Speed & Delivery
6. **YAMA** - Compliance & Governance
7. **KUBERA** - Commerce & Operations
8. **ASHWINI** - Healthcare & System Wellness
9. **BRIHASPATI** - Wisdom & Strategic Planning
10. **CHANDRA** - Analytics & Insights
11. **KARTIKEYA** - Leadership & Command
12. **MARUT** - Communication & Messaging
13. **NARADA** - Information & Knowledge Dissemination
14. **RUDRA** - Transformation & Change Management
15. **TVASHTA** - Creation & Design

### External Departments (5)
1. **SURYA** - Energy & EV Charging (URGAA)
2. **BRAHMA** - Creation & Product Innovation
3. **SARASWATI** - Knowledge, Learning & Content
4. **VARUNA** - Communication & Customer Relations
5. **PRAGYA** - Intelligence & Research

---

## 🔄 Daily Learning Pipeline

### Execution Flow
```
06:00 UTC (Daily)
    ↓
Celery Beat Trigger
    ↓
For each department (20):
    1. Query Perplexity API with department-specific query
    2. Receive real-time intelligence with citations
    3. Process with Claude LLM to extract relevant insights
    4. Save to dated files
    5. Wait 2 seconds (rate limiting)
    ↓
Generate Summary Report
    ↓
Complete (Total time: ~60-90 seconds)
```

### Manual Trigger
**API Endpoint**: `POST /api/knowledge/trigger-learning`
**Auth**: Admin/CEO only
**Response**: Task started confirmation

---

## 📡 API Endpoints

### 1. Get All Departments
```bash
GET /api/knowledge/departments
Authorization: Bearer {token}
```

**Response**:
```json
{
  "internal": ["lakshmi", "vishwakarma", ...],
  "external": ["surya", "brahma", ...]
}
```

### 2. Query Department Knowledge
```bash
POST /api/knowledge/query
Authorization: Bearer {token}
Content-Type: application/json

{
  "department": "lakshmi",
  "include_pre_data": true,
  "include_post_data": true,
  "days_back": 7
}
```

**Response**:
```json
{
  "department": "lakshmi",
  "scope": "internal",
  "pre_data": {
    "domain_expertise": "# LAKSHMI - Financial Management...",
    "rules": {...},
    "policies": "# LAKSHMI Department - Financial Policies...",
    "sop": "# LAKSHMI Department - Standard Operating Procedures..."
  },
  "post_data": [
    {
      "department": "lakshmi",
      "timestamp": "2025-12-15T23:56:20.579247+00:00",
      "query": "Latest trends in fintech...",
      "processed_intelligence": "Overall trends in fintech...",
      "citations": ["https://...", "https://..."]
    }
  ],
  "last_updated": "2025-12-15T23:57:00.000000"
}
```

### 3. Get Daily Digest
```bash
GET /api/knowledge/daily-digest/{date}
Authorization: Bearer {token}

Example: GET /api/knowledge/daily-digest/2025-12-15
```

**Response**:
```json
{
  "date": "2025-12-15",
  "summary": {
    "timestamp": "2025-12-15T23:50:58.819965+00:00",
    "total_departments": 20,
    "successful": 20,
    "failed": 0
  },
  "departments": {
    "lakshmi": {...},
    "vishwakarma": {...},
    ...
  }
}
```

### 4. Trigger Learning Pipeline
```bash
POST /api/knowledge/trigger-learning
Authorization: Bearer {token}
```

**Response**:
```json
{
  "status": "started",
  "message": "Daily learning pipeline started in background"
}
```

---

## 🔧 Technical Implementation

### Technologies Used
- **API Framework**: FastAPI
- **Task Queue**: Celery + Redis (for scheduled tasks)
- **Intelligence Source**: Perplexity API (Sonar model)
- **LLM Processing**: Claude via Emergent Integrations
- **Storage**: File system (JSON + Markdown)
- **Future**: Vector database (Pinecone) for semantic search

### Environment Variables
```bash
# Required
PERPLEXITY_API_KEY=pplx-xxx
EMERGENT_LLM_KEY=sk-emergent-xxx
REDIS_URL=redis://localhost:6379/0

# Optional
KNOWLEDGE_RETENTION_DAYS=90
```

### File Sizes
- Pre-Data: ~80 KB total (84 files)
- Post-Data: ~500-800 KB per day (20 departments)
- Estimated monthly storage: ~15-25 MB

---

## 🚀 Usage Examples

### Example 1: Get Latest Financial Intelligence
```python
import requests

API_URL = "https://kailash-ai.in/api"
TOKEN = "your_jwt_token"

# Query LAKSHMI department knowledge
response = requests.post(
    f"{API_URL}/knowledge/query",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={
        "department": "lakshmi",
        "include_pre_data": True,
        "include_post_data": True,
        "days_back": 3
    }
)

knowledge = response.json()
print(f"Latest Intelligence: {knowledge['post_data'][0]['processed_intelligence']}")
```

### Example 2: Trigger Manual Learning
```python
response = requests.post(
    f"{API_URL}/knowledge/trigger-learning",
    headers={"Authorization": f"Bearer {TOKEN}"}
)

print(response.json()['message'])
```

---

## 📈 Performance Metrics

- **Pipeline Execution Time**: 60-90 seconds for all 20 departments
- **API Response Time**: < 200ms for knowledge queries
- **Data Freshness**: Updated daily at 06:00 UTC
- **Success Rate**: 100% (20/20 departments in latest run)
- **Storage Growth**: ~500-800 KB per day

---

## 🔮 Future Enhancements

### Phase 3: Vector Database Integration (Planned)
- Implement Pinecone for semantic search
- Enable natural language queries across all knowledge
- Build knowledge graph for cross-department insights
- Real-time knowledge updates (beyond daily batch)

### Phase 4: Frontend Integration (Planned)
- Display Pre-Data on department detail pages
- Show latest daily intelligence summaries
- Knowledge search interface
- Intelligence trend visualization
- Citation browsing

---

## 🎓 Best Practices

1. **Pre-Data Updates**: Review and update quarterly
2. **Post-Data Retention**: Keep 90 days of intelligence
3. **Manual Triggers**: Use sparingly (rate limits apply)
4. **Error Monitoring**: Check daily digest summaries
5. **Cost Management**: Monitor Perplexity API usage

---

## 🛠️ Maintenance

### Daily Tasks (Automated)
- ✅ Run daily learning pipeline at 06:00 UTC
- ✅ Generate intelligence for all 20 departments
- ✅ Create daily digest summary
- ✅ Archive previous day's data

### Weekly Tasks
- Review success/failure rates
- Check storage usage
- Monitor API costs
- Validate data quality

### Quarterly Tasks
- Update Pre-Data knowledge files
- Review and refine department queries
- Optimize LLM processing prompts
- Audit and cleanup old data

---

## 📞 Support

For issues or questions about the Knowledge Architecture:
- Technical Issues: Check backend logs at `/var/log/supervisor/backend.*.log`
- API Documentation: Visit `/api/docs` for interactive API documentation
- Knowledge Files: Located at `/app/backend/knowledge/`

---

## 🎉 Implementation Status

✅ **Phase 1 COMPLETE**: Pre-Data Foundation (84 knowledge files)
✅ **Phase 2 COMPLETE**: Daily Learning Pipeline (Perplexity + Claude)
✅ **Phase 3 COMPLETE**: Knowledge Retrieval APIs (4 endpoints)
⏳ **Phase 4 PENDING**: Frontend Integration
⏳ **Phase 5 PENDING**: Vector Database for Semantic Search

---

**Last Updated**: December 15, 2025
**Version**: 1.0.0
**Status**: Production Ready 🚀
