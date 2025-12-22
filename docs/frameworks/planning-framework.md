# Planning Framework (GIST)

## Übersicht

Planning nach dem **GIST Framework** (von Itamar Gilad, ex-Google/Spotify):
- **G**oals = Was wollen wir erreichen?
- **I**deas = Wie könnten wir es tun?
- **S**trategy = Wie setzen wir es um?
- **T**asks/Steps = Was bauen wir, wann?

---

## Warum GIST?

**Pro:**
- ✅ Strukturiert, aber nicht heavyweight
- ✅ Fokus auf Entscheidungen, nicht Dokumentation
- ✅ Bewährt bei Spotify, Google, vielen Startups
- ✅ Kombiniert mit Decision Log (GitLab, Shopify)

**Contra andere Frameworks:**
- ❌ Business Cases: Zu viel Overhead
- ❌ Stage-Gate: Zu langsam
- ❌ PRDs (Product Requirements Doc): Veralten schnell

---

## Planning-Struktur: Question-driven Iterations

**Idee:** Nach Base Research hast du **offene Fragen**. Statt alles auf einmal zu beantworten, bearbeitest du **eine Frage nach der anderen**.

**Typische Questions (aus Base Research):**
- Welches Frontend Framework sollten wir nutzen? (aus Technical Research)
- Local-first oder Hybrid Architecture? (aus Technical Research)
- Welches Segment priorisieren wir zuerst? (aus Market Research)
- Freemium oder Paid-only Model? (aus Monetization Research)
- Welche Features gehören in MVP vs. Phase 2? (aus Product-User Fit Research)
- Soft Launch oder Big Bang Launch? (aus GTM Research)

**Question Categories:** (identisch mit Base Research Kategorien)
1. Technical Feasibility Questions
2. Market Opportunity Questions
3. Monetization Questions
4. Legal & Risk Questions
5. Product-User Fit Questions
6. Go-to-Market Questions

**Eine Question = Eine Iteration = Ein File**

**WICHTIG:** Questions werden aus Base Research extrahiert (siehe `iteration-planning.md`)

---

## Iteration Structure (pro Question)

```markdown
# I00X: [Question]

**Question:** [Die konkrete Frage, die beantwortet werden soll]
**Question ID:** Q00X (aus question-backlog.md)
**Category:** [1-6, welche Research-Kategorie]
**Priority:** [RICE Score aus Question Backlog]
**Status:** In Progress / Complete

---

## 1. Research (aus Base Research)

**Relevant Research:**
[Links zu relevanten Base Research Files die diese Question informieren]
[Key findings aus 0-base-research/]

## 2. Goals (aus Question abgeleitet)

**Question:** [Wiederholen für Kontext]

**Abgeleitete Goals:**
- Business Goals (Was erreichen wir geschäftlich?)
- User Goals (Was erreichen wir für User?)
- Technical Goals (Was erreichen wir technisch?)
- Team Goals (Was erreichen wir für Team/Org?)

## 3. Ideas (Mögliche Antworten/Lösungen)

**Was sind mögliche Lösungen/Antworten auf die Question?**

[Liste von Ideas/Lösungen mit RICE Scoring]

**WICHTIG:** Dies ist RICE Ebene 2 (Lösungen innerhalb einer Question).
Ebene 1 war: Welche Question zuerst? (im question-backlog.md)

## 4. Strategy (Wie setzen wir es um?)
- Technical Strategy
- Marketing Strategy
- Positioning Strategy

## 5. Roadmap (Wann bauen wir was?)
- MVP
- Phase 1
- Phase 2

## 6. Metrics (Wie messen wir?)
- Success Metrics
- Business Metrics
- Technical Metrics

## 7. Decision (Answer to Question)

**Question:** [Die ursprüngliche Frage]
**Answer:** [Die finale Antwort/Entscheidung]
**Decision ID:** D00X

[Finale Decision mit Rationale + Implementation Links]

**Routing:** (siehe Decision Router unten)
- Category: [1-6]
- Output File: `3-output/decisions-[category].md`
- Handoff: [technical-dev-kit / other]
```

**Alles in EINEM File!** (z.B. `I001-thema-name.md`)

---

## GIST Framework: Details

### 1. Goals (Was wollen wir erreichen?)

**Fragen:**
- Was ist Erfolg für dieses Thema?
- Welche Business-Metriken wollen wir bewegen?
- Was brauchen User?
- Was sind technische Constraints?

**Format:**
```markdown
## Goals

### Business Goals
- [Revenue target from key segment]
- [Competitive advantage description]

### User Goals
- [User benefit 1]
- [User benefit 2]

### Technical Goals
- [Technical constraint 1]
- [Architecture requirement]
```

**Example (AI Tutoring App - Privacy Thema):**
```markdown
### Business Goals
- €50K ARR from privacy-conscious segment
- Privacy moat vs. competitors

### User Goals
- 100% data privacy guarantee
- Trust + parent control

### Technical Goals
- Zero network requests during tutoring
- Local-first architecture
```

---

### 2. Ideas (Wie könnten wir es tun?)

**Fragen:**
- Welche Features/Ansätze könnten die Goals erreichen?
- Was sind Alternativen?
- Quick wins vs. big bets?

**RICE Scoring:**
- **R**each: Wie viele User betrifft es? (1-10)
- **I**mpact: Wie groß ist der Effekt? (1-10)
- **C**onfidence: Wie sicher sind wir? (1-10)
- **E**ffort: Wie viel Aufwand? (1-10, höher = mehr Aufwand)

**RICE Score = (R × I × C) / E**

**Format:**
```markdown
## Ideas (RICE Scoring)

| Idea | Reach | Impact | Confidence | Effort | RICE Score |
|------|-------|--------|------------|--------|------------|
| [Idea 1] | X | X | X | X | XX.XX |
| [Idea 2] | X | X | X | X | XX.XX ✅ QUICK WIN |

## Prioritization
1. [Idea A] (Reason, RICE score)
2. [Idea B] (Reason, RICE score)
```

**Example (AI Tutoring App - Privacy Thema):**
```markdown
| Idea | Reach | Impact | Confidence | Effort | RICE Score |
|------|-------|--------|------------|--------|------------|
| Local LLM | 10 | 10 | 8 | 6 | 18.75 |
| Network viewer | 7 | 6 | 9 | 2 | 21.00 ✅ QUICK WIN |

## Prioritization
1. Network viewer (Quick win, low effort, RICE 21.00)
2. Local LLM (Foundation feature, RICE 18.75)
```

---

### 3. Strategy (Wie setzen wir es um?)

**Fragen:**
- Wie setzen wir die priorisierten Ideas um?
- Was ist die technische Strategie?
- Wie vermarkten wir es?
- Wie mitigieren wir Risks?

**Format:**
```markdown
## Strategy

### Technical Strategy
- [Technology choice 1]
- [Framework/Platform choice]
- [Data storage approach]

### Marketing Strategy
- Channels: [Channel 1, Channel 2, Channel 3]
- Content: [Content type 1, Content type 2]

### Positioning Strategy
- Tagline: [Your tagline]
- Moat: [How competitors can't easily copy]
```

**Example (AI Tutoring App - Privacy Thema):**
```markdown
### Technical Strategy
- Llama 3.1 8B (local inference)
- Electron (cross-platform desktop)
- SQLite (local storage)

### Marketing Strategy
- Channels: r/privacy, r/homeschool, HackerNews
- Content: "How to verify AI privacy", "GDPR compliance guide"

### Positioning Strategy
- Tagline: "Your child's data never leaves your device"
- Moat: Privacy-by-design (competitors can't easily copy local-first architecture)
```

---

### 4. Roadmap (Wann bauen wir was?)

**Fragen:**
- Was bauen wir im MVP?
- Was kommt in Phase 1, 2, 3?
- Was ist Must-Have vs. Nice-to-Have?

**MoSCoW Prioritization:**
- **M**ust have (MVP)
- **S**hould have (Phase 1)
- **C**ould have (Phase 2)
- **W**on't have (Backlog)

**Format:**
```markdown
## Roadmap

### MVP (Must Have) - Months 1-3
- [Core feature 1]
- [Core feature 2]
- [Core feature 3]

### Phase 1 (Should Have) - Months 3-6
- [Enhanced feature 1]
- [Enhanced feature 2]

### Phase 2 (Could Have) - Months 6-12
- [Advanced feature 1]
- [Advanced feature 2]

### Backlog (Won't Have for now)
- [Deferred feature]
```

**Example (AI Tutoring App - Privacy Thema):**
```markdown
### MVP (Must Have) - Months 1-3
- Local LLM (Llama 3.1 8B)
- Network traffic viewer
- Basic parental dashboard

### Phase 1 (Should Have) - Months 3-6
- Offline mode (no internet required)
- Privacy audit logs

### Phase 2 (Could Have) - Months 6-12
- Open-source core
- Third-party privacy audits

### Backlog (Won't Have for now)
- Multi-device sync (conflicts with privacy goals)
```

---

### 5. Metrics (Wie messen wir?)

**Fragen:**
- Woran messen wir Erfolg?
- Welche KPIs tracken wir?
- Was sind realistische Targets?

**Format:**
```markdown
## Metrics

### Adoption Metrics
- [Adoption metric description]
- Target: [X%]

### User Metrics
- [User satisfaction metric]
- Target: [Score]

### Technical Metrics
- [Technical performance metric]
- Target: [Value]

### Business Metrics
- CAC: Target [€X]
- LTV: Target [€Y]
- [Other business metric]: Target [Value]
```

**Example (AI Tutoring App - Privacy Thema):**
```markdown
### Adoption Metrics
- % users who verify network traffic
- Target: 60%

### User Metrics
- NPS among privacy-conscious parents
- Target: 50+

### Technical Metrics
- Network requests during tutoring
- Target: 0

### Business Metrics
- CAC from privacy channels: €10-20
- LTV privacy segment: €360
- Conversion rate (free to paid): 10%
```

---

### 6. Decision (Finale Entscheidung)

**Format:** (Basierend auf GitLab/Shopify Decision Log)

```markdown
## Decision D00X: Decision Name

**Date:** YYYY-MM-DD
**Status:** APPROVED ✅ / REJECTED ❌ / DEFERRED ⏸️
**Owner:** Product Management

### Context
[Warum brauchen wir diese Decision?]

### Options Considered
1. Option A (chosen) ✅
2. Option B
3. Option C

### Decision
[Was haben wir entschieden und warum?]

### Consequences
✅ Positive
⚠️ Risks/Trade-offs

### Implementation
→ Links to technical-dev-kit/iterations/
→ Links to execution plans

### Metrics
[Wie tracken wir ob die Decision richtig war?]

---
**Next Iteration:** I00X-naechstes-thema
```

---

## Workflow: Von Question zu Decision

```
1. Base Research abschließen
   (Alle 6 Kategorien, 24 Sub-Kategorien)

2. Questions extrahieren
   → Siehe iteration-planning.md
   → Create: 2-working-state/question-backlog.md

3. Questions priorisieren (RICE Scoring)
   → Welche Question zuerst beantworten?

4. Top Priority Question wählen
   → Create: 2-working-state/2-iterations/I00X-question.md

5. GIST Framework durchgehen
   Question → Research → Goals → Ideas (RICE) → Strategy → Roadmap → Metrics → Decision

6. Decision dokumentieren
   → Decision ID: D00X
   → Route to output (siehe Decision Router)

7. Update question-backlog.md
   → Mark question as answered
   → Pick next priority question

8. Wiederholen bis key questions beantwortet
```

**Example Workflow:**
```
1. Base Research: Complete ✅
2. Extract Questions: 12 questions identified
3. Prioritize: Q002 "Local vs Hybrid?" (RICE 16.0) = Top Priority
4. Create: I001-architecture-decision.md
5. GIST: Question → Goals → Ideas (React/Vue/Svelte) → Decision
6. Document: D001 "Local-first Architecture" → Route to decisions-technical.md
7. Update backlog: Q002 answered ✅, next: Q009 "MVP Scope?"
8. Repeat: I002-mvp-scope.md
```

---

## Exit Criteria: Iteration Complete

- [ ] Goals klar definiert
- [ ] Ideas mit RICE bewertet
- [ ] Strategy dokumentiert
- [ ] Roadmap erstellt (MVP + Phasen)
- [ ] Metrics definiert (mit Targets)
- [ ] **Decision dokumentiert** ✅

**Output:** Decision Document (D00X-name.md) → Handoff to Technical

---

## Best Practices

### Iteration Scope
- **Ein Thema = Ein File** (nicht überkomplex)
- **Zeit-boxen** - Max. 1 Woche pro Iteration
- **Fokus auf Decision** - Ziel ist eine klare Entscheidung

### RICE Scoring
- **Ehrlich sein** - Confidence oft niedriger als gedacht
- **Relative Scores** - Vergleich zwischen Ideas, nicht absolute Zahlen
- **Quick Wins** - RICE >15 mit low effort = sofort machen

### Decision Quality
- **Optionen zeigen** - Was haben wir NICHT gewählt und warum?
- **Consequences ehrlich** - Was sind Risks/Trade-offs?
- **Reversible?** - Können wir die Decision ändern? (meist ja!)

---

## Complete Example

For a complete iteration example, see the backup directory:
`product-management-ai-tutoring-backup/2-working-state/iterations/I001-privacy.md`

---

---

## Decision Router (Wohin mit Decisions?)

Nach jeder Iteration hast du eine **Decision** (Answer to Question). Je nach **Category** wird die Decision geroutet:

### Routing nach 6 Kategorien

**Category 1: Technical Feasibility**
- **Example Questions:** Welches Framework? Local vs Hybrid? Performance Targets?
- **Routing:**
  1. ✅ Log in `3-output/decisions-technical.md`
  2. ✅ Log in `3-output/decision-log.md` (Master Index)
  3. ✅ Handoff to `technical-dev-kit/1-description/HANDOFF_FROM_PLANNING.md`
  4. ✅ Update `mvp-definition.md` (if affects MVP)

---

**Category 2: Market Opportunity**
- **Example Questions:** Welches Segment priorisieren? Wie vs. Competitor X positionieren?
- **Routing:**
  1. ✅ Log in `3-output/decisions-market.md`
  2. ✅ Log in `3-output/decision-log.md`
  3. ✅ Update GTM strategy (affects channels, messaging)

---

**Category 3: Monetization**
- **Example Questions:** Freemium vs Paid? €19.99 oder €29.99/mo?
- **Routing:**
  1. ✅ Log in `3-output/decisions-monetization.md`
  2. ✅ Log in `3-output/decision-log.md`
  3. ✅ Update `business-model.md` (pricing, revenue strategy)

---

**Category 4: Legal & Risk**
- **Example Questions:** Self-certification oder Third-party audit? GDPR timeline?
- **Routing:**
  1. ✅ Log in `3-output/decisions-legal-risk.md`
  2. ✅ Log in `3-output/decision-log.md`
  3. ✅ Update compliance timeline in roadmap

---

**Category 5: Product-User Fit**
- **Example Questions:** MVP Scope? Welche Features Must-Have? Onboarding Flow?
- **Routing:**
  1. ✅ Log in `3-output/decisions-product.md`
  2. ✅ Log in `3-output/decision-log.md`
  3. ✅ Update `mvp-definition.md` (features, user stories)
  4. ✅ Handoff to technical-dev-kit (if UI/UX specs needed)

---

**Category 6: Go-to-Market**
- **Example Questions:** Launch Strategy? Channel Priority? Messaging?
- **Routing:**
  1. ✅ Log in `3-output/decisions-gtm.md`
  2. ✅ Log in `3-output/decision-log.md`
  3. ✅ Update `gtm-plan.md` (channels, launch timeline)

---

### Master Decision Log

**3-output/decision-log.md** = Central Index

**ALL decisions logged here** with:
- Decision ID (D00X)
- Question ID (Q00X)
- Category (1-6)
- Answer (short)
- Link to full decision in category file
- Link to iteration file (I00X)
- Status (Approved / Deferred / Rejected)

**Purpose:** Quick reference, chronological log, cross-linking

---

**Nächster Schritt:** Nach allen Key-Iterations → Consolidate to `mvp-definition.md` → Handoff to Technical Dev Kit
