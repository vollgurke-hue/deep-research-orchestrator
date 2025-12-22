# Research Framework

## Übersicht

Das Research Framework definiert, wie wir systematisch Research betreiben, um fundierte Produktentscheidungen zu treffen.

---

## 6-Category Research Framework (CORE CONCEPT)

**Warum 6 Kategorien?**
Um ein Produkt vollständig zu validieren, beantworten wir 6 fundamentale Fragen:

### 1. Technical Feasibility
**Kernfrage:** Can we build it?

**Sub-Categories (5):**
- Tech Stack Options
- Architecture & Data Flow
- Performance Requirements
- Hardware & Infrastructure
- Development Timeline & Resources

**Warum wichtig?** Technische Machbarkeit ist Grundvoraussetzung.

---

### 2. Market Opportunity
**Kernfrage:** Is there a market?

**Sub-Categories (4):**
- Market Size (TAM/SAM/SOM)
- Target Segments
- Competitive Landscape
- Market Trends & Growth

**Warum wichtig?** Kein Markt = kein Produkt.

---

### 3. Monetization & Economics
**Kernfrage:** Can we make money?

**Sub-Categories (4):**
- Pricing Models
- Unit Economics (CAC, LTV, Margins)
- Cost Structure
- Revenue Projections & Scenarios

**Warum wichtig?** Viability requires profitability.

---

### 4. Legal & Risk
**Kernfrage:** Can we legally operate?

**Sub-Categories (3):**
- Legal Requirements (GDPR, COPPA, etc.)
- Compliance & Certifications
- Risk Assessment

**Warum wichtig?** Legal blockers können das Produkt killen.

---

### 5. Product-User Fit
**Kernfrage:** Do users want it?

**Sub-Categories (4):**
- User Personas
- Pain Points & Jobs-to-be-Done
- Product Features (core, differentiating, nice-to-have)
- UX Patterns & Customer Journey

**Warum wichtig?** Features ohne User Needs = Failure.

---

### 6. Go-to-Market
**Kernfrage:** How do we reach users?

**Sub-Categories (4):**
- Marketing Channels
- Content & Messaging Strategy
- Sales Strategy (B2B/B2C)
- Launch Plan & Timeline

**Warum wichtig?** Great product, zero distribution = failure.

---

**Framework Benefits:**
- ✅ Comprehensive coverage (24 sub-categories)
- ✅ Industry-standard structure
- ✅ Cross-dependency tracking built-in
- ✅ Research provides OPTIONS, Planning makes DECISIONS

---

## Research-Phasen

### Phase 0: Base Research (6-Category Framework)

**Ziel:** Systematische Research in allen 6 Kategorien durchführen.

**Recommended Order:**
1. Technical Feasibility (understand constraints first)
2. Market Opportunity (validate market exists)
3. Monetization (confirm business model viable)
4. Legal & Risk (identify blockers early)
5. Product-User Fit (validate user needs)
6. Go-to-Market (plan distribution)

**Dauer:** 1-2 Wochen (for all 6 categories)

**Vorgehen:**
1. Start with Category 1 (Technical Feasibility)
2. For each sub-category: Read [SubCategory]_Vorgehen.md
3. Follow research methods, use templates
4. Document in `2-working-state/0-base-research/[category]/[sub-category].md`
5. Validate with exit_criteria.json
6. Check cross-dependencies → update planning_state.json if needed
7. Move to next sub-category / category

**Output:** 24 research files in `2-working-state/0-base-research/`

**Cross-Dependencies:** Actively tracked! Findings in one category may require re-evaluation of others.

---

### Phase 1 (Optional): Validation

**Ziel:** Validate key assumptions before planning.

**Options:**
- **POC (Proof of Concept):** Validate 1-2 critical technical unknowns
- **User Interviews:** Validate pain points, WTP, features
- **Market Tests:** Landing page, pre-sales, competitor analysis

**When to do:** If research has LOW confidence levels in critical areas

**Duration:** 1-5 days per validation activity

**Output:** Validation reports → update research files with findings

---

## Research-Methoden

### Desk Research
- Web-Suche (Market reports, competitor websites, news)
- Industry reports (Gartner, Grand View Research, etc.)
- Academic papers
- Regulatory documents

### Competitive Analysis
- Feature comparison matrix
- Pricing analysis
- User reviews (App Store, Reddit, etc.)
- Traffic analysis (SimilarWeb, etc.)

### User Research
- Surveys (Google Forms, Typeform)
- Interviews (1-on-1 Gespräche)
- Community listening (Reddit, Forums)
- Pain point analysis

---

## Exit Criteria: Base Research Complete

**All 6 categories complete when:**

- [ ] **Category 1: Technical Feasibility** - All 5 sub-categories complete
- [ ] **Category 2: Market Opportunity** - All 4 sub-categories complete
- [ ] **Category 3: Monetization** - All 4 sub-categories complete
- [ ] **Category 4: Legal & Risk** - All 3 sub-categories complete
- [ ] **Category 5: Product-User Fit** - All 4 sub-categories complete
- [ ] **Category 6: Go-to-Market** - All 4 sub-categories complete

**Validation:**
- [ ] All 24 sub-category working files filled out
- [ ] All CRITICAL exit criteria passed (per sub-category's exit_criteria.json)
- [ ] Cross-dependencies identified and documented in planning_state.json
- [ ] Confidence levels marked (HIGH/MEDIUM/LOW) for key assumptions
- [ ] Sources cited (minimum 2 per sub-category)

**GO/NO-GO Decision:**
- [ ] Market size sufficient (SOM ≥ target revenue)
- [ ] Unit economics viable (LTV:CAC ≥ 3:1)
- [ ] No critical legal/risk blockers
- [ ] Product-market fit validated (user pain points confirmed)

**Next Phase:** Review Phase - siehe unten

---

### Phase 2: Base Research Review Phase ⭐ NEW

**Ziel:** Gesamtbild erfassen BEVOR Planning beginnt. Lücken schließen, Inkonsistenzen beheben.

**Warum kritisch?**
- ✅ Verhindert übersehene Aspekte in Planning Phase
- ✅ Stellt sicher, dass alle 6 Kategorien konsistent sind
- ✅ Identifiziert finale Lücken bevor Questions extrahiert werden
- ✅ Ermöglicht strategisches "Big Picture" Denken
- ✅ Entdeckt Themen die **Research Excurse** brauchen

**Dauer:** 1-2 Tage (schneller Review aller Kategorien) + optional Excurse (je 1-4 Stunden)

**Vorgehen:**

**Schritt 1: Category-by-Category Review**
1. Öffne jede Kategorie (1-6) der Reihe nach
2. Lese alle Sub-Category Files schnell durch
3. Checke:
   - [ ] Sind alle TODOs abgeschlossen?
   - [ ] Sind Confidence-Levels realistisch?
   - [ ] Fehlen wichtige Informationen?
   - [ ] Gibt es Widersprüche zwischen Sub-Categories?
4. Füge fehlende Infos hinzu / fixe Inkonsistenzen
5. Markiere als "REVIEWED ✅"

**Schritt 2: Cross-Category Consistency Check**
- [ ] Technical Constraints vs Market Size konsistent?
   - Beispiel: "8GB RAM requirement → reduziert TAM um X%"
- [ ] Pricing vs Unit Economics realistisch?
   - Beispiel: "€19.99/mo → CAC €50 viable bei LTV €240?"
- [ ] Product Features vs GTM Channels aligned?
   - Beispiel: "Privacy feature → r/privacy channel"
- [ ] Timeline vs Legal Requirements realistisch?
   - Beispiel: "GDPR compliance → +2 Monate dev time"

**Schritt 3: Big Picture Questions**
- [ ] **Thesis Validation:** Macht das Gesamtbild Sinn?
- [ ] **Moat Check:** Haben wir einen Competitive Moat?
- [ ] **Risk Check:** Gibt es Hidden Blockers?
- [ ] **Opportunity Check:** Haben wir die Opportunity richtig verstanden?

**Schritt 4: Planning_State.json Update**
```json
{
  "current": {
    "phase": "0-base-research-review",
    "status": "in_progress",
    "review_progress": {
      "1-technical-feasibility": "reviewed",
      "2-market-opportunity": "in_progress",
      "3-monetization": "not_started",
      ...
    }
  }
}
```

**Output:**
- [ ] Alle 6 Kategorien reviewed und konsistent
- [ ] Offene Fragen/Lücken dokumentiert für Planning Phase
- [ ] planning_state.json updated: `phase: "0-base-research-review-complete"`
- [ ] Bereit für Question Extraction

**Exit Criteria:**
- [ ] Alle 24 Sub-Categories REVIEWED ✅
- [ ] Cross-dependencies validiert
- [ ] Keine kritischen Lücken mehr
- [ ] Team-Confidence: "Wir verstehen das Big Picture"

**Next Phase:** Question Extraction → Planning (GIST Iterations) - siehe `planning-framework.md`

---

### Phase 2.5: Research Excurse (Optional, bei Bedarf) ⭐ NEW

**Was sind Research Excurse?**

Research Excurse sind **tiefere Recherchen zu spezifischen Themen**, die während der Review Phase entdeckt werden.

**Unterschied zu Base Research und Validation:**

| Typ | Zweck | Wann | Beispiel |
|-----|-------|------|----------|
| **Base Research** | Breites Fundament in 6 Kategorien | Phase 0 | Market Size, Tech Stack, Pricing |
| **Validation** | Hypothesen testen (POC, User Interviews) | Phase 1 (optional) | POC App, User Interviews, Landing Page Test |
| **Research Excurse** | Spezifische Lücken/Widersprüche klären | Phase 2 Review | Q-Chat Failure Analysis, Hardware-Konflikt |

**Wann nutzen?**

Während Review Phase entdeckst du:
- ✅ **Widersprüche** zwischen Kategorien (z.B. "Tech sagt 30%, Market sagt 65%")
- ✅ **Lücken** im Verständnis (z.B. "WARUM ist Q-Chat gescheitert?")
- ✅ **Tiefere Fragen** zu Konkurrenten, Models, Strategien
- ✅ **Komplexe Trade-offs** die mehr Research brauchen

**Excurse Kriterien:**
- ⏱️ **Zeitboxed:** 1-4 Stunden pro Excurse (nicht Wochenlang!)
- 🎯 **Fokussiert:** Eine konkrete Frage beantworten
- 📝 **Dokumentiert:** Eigenes File in `2-working-state/research-excurse/`
- ✅ **Actionable:** Ergebnis informiert Planning Decisions

**Beispiele (aus AI Tutoring Projekt):**

**Excurse 1: Model Comparison Research**
- **Trigger:** Review entdeckte: "Sollten wir alternatives LLM nutzen?"
- **Frage:** Gibt es besseres 7-8B Modell als Llama 3.1:8b?
- **Methode:** Benchmark-Research, Ollama-Check, License-Verify
- **Dauer:** 2 Stunden (Agent-gestützt)
- **Ergebnis:** "Stay with Llama" + Review-Triggers definiert
- **File:** `research-excurse/model-comparison-research.md`

**Excurse 2: Q-Chat Failure Analysis**
- **Trigger:** Review sah: "Q-Chat discontinued after 2 years - WHY?"
- **Frage:** Was können wir aus Q-Chat Scheitern lernen?
- **Methode:** Press releases, Reddit/HN discussions, industry analysis
- **Dauer:** 1-2 Stunden
- **Ergebnis:** "API costs + insufficient differentiation" → Lessons for Pricing/Positioning
- **File:** `research-excurse/q-chat-failure-analysis.md`

**Excurse 3: Hardware Market Sizing Conflict**
- **Trigger:** Review fand: "Market sagt 65% capable, Tech sagt 30% optimal"
- **Frage:** Wie viel % des Marktes hat WIRKLICH geeignete Hardware?
- **Methode:** Hardware surveys, Steam Hardware Survey, Consumer reports
- **Dauer:** 1 Stunde
- **Ergebnis:** "35% GPU-optimal, 30% CPU-acceptable → 65% total viable"
- **File:** `research-excurse/hardware-market-sizing.md`

---

**Vorgehen:**

**Schritt 1: Excurse identifizieren (während Review)**
- Notiere Fragen/Widersprüche während Category Review
- Priorisiere: Welche sind **kritisch für Planning**?

**Schritt 2: Excurse durchführen**
```markdown
# [Excurse Title]

**Trigger:** [Was hat diesen Excurse ausgelöst?]
**Question:** [Die spezifische Frage]
**Duration:** [Zeitbudget: 1-4 Stunden]

## Research Method
[Wie researchen wir das?]

## Findings
[Was haben wir gelernt?]

## Implications
**For Planning:**
- [Was bedeutet das für Decisions?]

**For Base Research:**
- [Müssen wir Base Research updaten?]

## Recommendation
[Klare Empfehlung für Planning Phase]
```

**Schritt 3: Base Research updaten (falls nötig)**
- Falls Excurse Fehler in Base Research findet → korrigieren
- Cross-References hinzufügen

**Schritt 4: Planning vorbereiten**
- Excurse-Findings fließen in Question Backlog
- Werden in Iterations referenziert

---

**Location:**
```
2-working-state/
├── 0-base-research/           ← Breites Fundament (6 Kategorien)
├── 1-validation/               ← Hypothesen-Tests (POC, User Interviews)
├── research-excurse/           ← NEW! Tiefere Themen-Research
│   ├── model-comparison-research.md
│   ├── q-chat-failure-analysis.md
│   └── hardware-market-sizing.md
├── 2-iterations/
└── 3-output/
```

---

**Best Practice:**
- ⏱️ **Timeboxing:** Max 4 Stunden pro Excurse (sonst wird's zu groß)
- 🎯 **Fokus:** Eine Frage, nicht 10
- 📋 **Liste:** Sammle Excurse-Ideas, priorisiere, mache nur Top 2-3
- ✅ **Action:** Excurse muss zu klarer Recommendation führen

**Anti-Pattern:**
- ❌ Excurse ohne klare Frage ("Lass uns alles über X researchen")
- ❌ Wochenlange Excurse (das ist neues Base Research, nicht Excurse)
- ❌ Excurse ohne Planning-Relevanz ("Nice to know" ≠ "Need to know")

---

**Next Phase:** Question Extraction → Planning (GIST Iterations) - siehe `planning-framework.md`

---

## Best Practices

### Research Dokumentation
- **Ein File pro Thema** (einfacher zu navigieren)
- **Quellen angeben** (Glaubwürdigkeit)
- **Confidence Level** (HIGH/MEDIUM/LOW)
- **Datum** (Research veraltet schnell)

### Research Scope
- **Nicht perfektionieren** - 80% reicht für Entscheidungen
- **Zeit-boxen** - Max. 1-2 Wochen für Base Research
- **Fokus auf Entscheidungen** - Was müssen wir wissen, um zu entscheiden?

### Research Updates
- **Quarterly Review** - Market/Competitive Landscape
- **Ad-hoc** - Bei Major Competitor Moves oder Regulatory Changes

---

## Tools

**Market Research:**
- Google (Web Search)
- Grand View Research, Future Market Insights (Reports)
- SimilarWeb, SEMrush (Traffic/SEO)
- Product Hunt, Crunchbase (Product launches)

**User Research:**
- Reddit, HackerNews, Forums (Pain points)
- App Store Reviews (User feedback)
- Google Forms (Surveys)

**Competitive:**
- Competitor websites
- Product demos (Free trials, Freemium)
- LinkedIn (Team size, hiring)

---

**Nächster Schritt:** Nach Base Research → Planning (siehe `planning-framework.md`)
