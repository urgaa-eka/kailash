# RAG ENRICHMENT GUIDE
## Expanding GANESHA's Knowledge Base

---

## CURRENT STATUS
- **Total Vectors**: 851
- **Coverage**: Basic department info, SOPs, policies
- **Gap**: Product-specific operational data

---

## PRIORITY DOCUMENTS TO ADD

### High Priority (Week 1)
1. **URGAA Operations Manual** (50 pages)
   - Charger troubleshooting guide
   - OCPP protocol documentation
   - Auto-rectification procedures
   - Escalation matrix

2. **GSTSAAS User Guide** (30 pages)
   - Workshop onboarding process
   - GST filing procedures
   - Inventory management workflows
   - Customer support scripts

3. **IGNITION App Documentation** (25 pages)
   - User journey maps
   - Feature specifications
   - Payment flow documentation
   - Error handling guide

### Medium Priority (Week 2)
4. **Financial Policies** (20 pages)
   - Expense approval workflows
   - Budget allocation rules
   - Invoice processing procedures
   - Cash flow management guidelines

5. **HR Policies** (15 pages)
   - Leave policies
   - Performance review process
   - Onboarding checklist
   - Code of conduct

6. **Sales Playbook** (30 pages)
   - Lead qualification criteria
   - Pricing strategies
   - Objection handling scripts
   - Deal closure process

### Low Priority (Week 3)
7. **Marketing Guidelines** (20 pages)
8. **Legal Templates** (25 pages)
9. **Compliance Checklists** (15 pages)
10. **Partnership Agreements** (20 pages)

---

## DOCUMENT COLLECTION TEMPLATE

For each document, collect:
```
- Title
- Category (Operations/Finance/HR/Sales/etc)
- Department Owner
- Last Updated Date
- File Format (PDF/DOCX/MD)
- Access Level (Public/Internal/Confidential)
```

---

## UPLOAD QUEUE CONFIGURATION

Edit `backend/scripts/rag_upload_script.py`:

```python
UPLOAD_QUEUE = [
    {
        "path": "/path/to/urgaa_operations_manual.pdf",
        "category": "operations",
        "department": "SURYA",
        "metadata": {"priority": "high", "version": "2.1"}
    },
    {
        "path": "/path/to/gstsaas_user_guide.pdf",
        "category": "operations",
        "department": "TVASHTA",
        "metadata": {"priority": "high", "version": "1.5"}
    }
]
```

---

## EXPECTED IMPACT

| Metric | Before | After Enrichment |
|--------|--------|------------------|
| RAG Vectors | 851 | 2,500+ |
| Query Accuracy | 85% | 95%+ |
| Response Confidence | Medium | High |
| Hallucination Rate | 5% | <1% |

---

## USAGE INSTRUCTIONS

1. Place documents in `/app/backend/knowledge/documents/`
2. Update `UPLOAD_QUEUE` in `rag_upload_script.py`
3. Run: `python backend/scripts/rag_upload_script.py`
4. Verify: Check vector count in analytics dashboard
