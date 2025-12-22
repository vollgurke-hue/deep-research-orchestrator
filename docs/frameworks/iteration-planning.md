# Iteration Planning: Von Base Research zu Questions

**Purpose:** Diese Anleitung zeigt wie du nach abgeschlossenem Base Research **offene Fragen** extrahierst und priorisierst.

---

## Überblick

Nach Base Research hast du:
- ✅ 6 Kategorien komplett researched
- ✅ 24 Sub-Kategorien dokumentiert
- ✅ Cross-Dependencies identifiziert

**Aber:** Du hast noch **keine Decisions getroffen**!

Base Research liefert **Optionen + Rankings**, aber keine **Antworten**.

**Nächster Schritt:** Questions extrahieren → Priorisieren → Beantworten (via GIST)

---

## Schritt 1: Questions extrahieren

### Wo finde ich Questions?

**In jedem Research File** gibt es typische Hinweise auf offene Questions:

#### 1. Technical Feasibility

**Source:** `2-working-state/0-base-research/1-technical-feasibility/`

**Typische Questions:**
- **Tech Stack:** "Welches Framework sollten wir nutzen: React (32/40), Vue (28/40) oder Svelte (25/40)?"
- **Architecture:** "Local-first oder Hybrid Architecture?"
- **Performance:** "Welche Performance Targets setzen wir: <2s Response oder <5s akzeptabel?"
- **Hardware:** "Minimum 8GB RAM oder auch 4GB mit Quantization?"
- **Timeline:** "3 Monate MVP realistisch oder 4-5 Monate?"

**Erkennungsmerkmal:** Research listet **mehrere Optionen mit Scores**, aber keine Empfehlung.

---

#### 2. Market Opportunity

**Source:** `2-working-state/0-base-research/2-market-opportunity/`

**Typische Questions:**
- **Market Size:** "Fokus auf Global TAM oder DACH zuerst?"
- **Segments:** "Welches Segment priorisieren: Privacy-conscious Parents (13M) oder Homeschool (2.5M)?"
- **Competition:** "Wie positionieren wir uns vs. ChatGPT? Vs. Khanmigo?"
- **Trends:** "Auf welchen Trend setzen: Privacy-Regulierung oder AI-Adoption?"

**Erkennungsmerkmal:** Research zeigt **Segmente, Competitors, Trends** → Du musst wählen.

---

#### 3. Monetization

**Source:** `2-working-state/0-base-research/3-monetization/`

**Typische Questions:**
- **Pricing:** "Freemium oder Paid-only? €19.99/mo oder €29.99/mo?"
- **Unit Economics:** "Welche CAC Targets: €10-20 (organic) oder €30-50 (paid ads)?"
- **Cost Structure:** "Cloud Hosting oder 100% local (zero cloud costs)?"
- **Revenue:** "Year 1 Target: €50K ARR oder €100K ARR?"

**Erkennungsmerkmal:** Research zeigt **Pricing Models, Unit Economics** → Du musst Model wählen.

---

#### 4. Legal & Risk

**Source:** `2-working-state/0-base-research/4-legal-risk/`

**Typische Questions:**
- **Legal:** "GDPR: Self-certification oder Third-party audit?"
- **Compliance:** "DPIA notwendig oder optional für local-only?"
- **Risk:** "Wie mitigieren wir Competitor Risk: Patents oder Speed?"

**Erkennungsmerkmal:** Research zeigt **Compliance Options, Risks** → Du musst Strategy wählen.

---

#### 5. Product-User Fit

**Source:** `2-working-state/0-base-research/5-product-user-fit/`

**Typische Questions:**
- **User Personas:** "Primary Persona: Privacy Parents oder Homeschool Parents?"
- **Pain Points:** "Wichtigster Pain Point: Datenschutz oder Pädagogik?"
- **Product Features:** "Welche Features in MVP: Parental Dashboard Must-Have oder Phase 2?"
- **UX Journey:** "Onboarding: Guided Tour oder Self-Discovery?"

**Erkennungsmerkmal:** Research zeigt **Features, Personas, UX Patterns** → Du musst priorisieren.

---

#### 6. Go-to-Market

**Source:** `2-working-state/0-base-research/6-go-to-market/`

**Typische Questions:**
- **Channels:** "Welcher Channel zuerst: Reddit, HackerNews oder Homeschool Forums?"
- **Content:** "Content Strategy: Educational (How-to) oder Thought Leadership?"
- **Sales:** "B2C Focus oder B2B (Schools) parallel?"
- **Launch:** "Soft Launch (Reddit Beta) oder Big Bang Launch?"

**Erkennungsmerkmal:** Research zeigt **Channels, Strategies** → Du musst Channel Mix wählen.

---

## Schritt 2: Questions dokumentieren

### Template: question-backlog.md

**Create:** `2-working-state/question-backlog.md`

**Structure:** Sortiert nach 6 Kategorien (wie Base Research)

```markdown
# Open Questions (aus Base Research)

**Last Updated:** [Date]
**Status:** 12 Questions identified, 0 answered

---

## 1. Technical Feasibility Questions

- [ ] **Q001:** Welches Frontend Framework: React, Vue oder Svelte?
  - **Source:** 1-technical-feasibility/1-tech-stack
  - **Why important:** Beeinflusst Team Velocity + Bundle Size + Hiring
  - **Options:** React (32/40), Vue (28/40), Svelte (25/40)

- [ ] **Q002:** Local-first oder Hybrid Architecture?
  - **Source:** 1-technical-feasibility/2-architecture
  - **Why important:** Definiert Privacy Moat vs. Performance Trade-off
  - **Options:** Local-first (100% privacy), Hybrid (better performance)

---

## 2. Market Opportunity Questions

- [ ] **Q003:** Welches Segment priorisieren?
  - **Source:** 2-market-opportunity/2-segments
  - **Options:** Privacy Parents (13M, high WTP), Homeschool (2.5M, community)

[... für alle 6 Kategorien]
```

---

## Schritt 3: Questions priorisieren (RICE)

### RICE Scoring für Questions

**Reminder:** Dies ist **Ebene 1 RICE** (welche Question zuerst?).
Später innerhalb einer Iteration: **Ebene 2 RICE** (welche Lösung für die Question?).

**RICE Kriterien:**
- **Reach:** Wie viele Bereiche betrifft diese Question? (1-10)
- **Impact:** Wie kritisch ist die Answer für Product Success? (1-10)
- **Confidence:** Wie sicher sind wir, dass wir gute Answer finden? (1-10)
- **Effort:** Wie viel Aufwand die Question zu beantworten? (1-10, höher = mehr)

**RICE Score = (Reach × Impact × Confidence) / Effort**

---

### Beispiel: Question Prioritization

```markdown
## Question Prioritization (RICE Scoring)

| ID | Question | Category | R | I | C | E | RICE | Priority |
|----|----------|----------|---|---|---|---|------|----------|
| Q002 | Local vs Hybrid? | Tech | 10 | 10 | 8 | 5 | **16.0** | **1** ✅ |
| Q009 | MVP Scope? | Product | 10 | 10 | 7 | 8 | 8.75 | 2 |
| Q006 | Freemium vs Paid? | Monetization | 8 | 9 | 6 | 4 | 10.8 | 3 |
| Q001 | Framework? | Tech | 10 | 8 | 9 | 3 | 24.0 | 4 |
| Q011 | Launch Strategy? | GTM | 7 | 7 | 5 | 6 | 4.08 | 5 |

**Next Iteration:** I001 - Q002 (Local vs Hybrid Architecture)
```

**Hinweise:**
- **Reach 10:** Betrifft alle User, alle Features, alle Decisions
- **Impact 10:** Mission-critical decision (z.B. Architecture, MVP Scope)
- **Confidence 8:** Base Research liefert gute Daten
- **Effort 5:** 1 Woche Iteration benötigt

---

## Schritt 4: Erste Question wählen

### Workflow

1. **Pick Top Priority Question** (höchster RICE Score)
2. **Create Iteration File:** `2-working-state/2-iterations/I001-question-slug.md`
3. **Copy Template** from `1-description/templates.md` (Iteration Template)
4. **Work through GIST:**
   - Question → Research → Goals → Ideas → Strategy → Roadmap → Metrics → Decision
5. **Document Decision** and route to output
6. **Update question-backlog.md:** Mark Q00X as answered
7. **Pick Next Question** and repeat

---

## Best Practices

### Question Formulation

❌ **Zu vage:** "Was machen wir mit Pricing?"
✅ **Konkret:** "Freemium (30 min/Woche free) oder Paid-only (€19.99/mo)?"

❌ **Zu breit:** "Wie launchen wir?"
✅ **Spezifisch:** "Soft Launch auf r/privacy oder Big Bang mit Product Hunt?"

❌ **Multiple Questions:** "Framework und Architecture und Timeline?"
✅ **Eine Question:** "Welches Frontend Framework?" (separate Iteration pro Question)

---

### Wieviele Questions?

**Typisch:** 10-20 Questions nach Base Research

**Must Answer (für MVP):**
- 2-3 Technical Questions (Stack, Architecture, Performance)
- 1-2 Market Questions (Segment, Positioning)
- 1-2 Monetization Questions (Pricing Model, Targets)
- 1 Legal/Risk Question (Compliance Strategy)
- 2-3 Product Questions (MVP Scope, Core Features, UX)
- 1-2 GTM Questions (Launch Strategy, Channel Priority)

**Nice to Answer (für Post-MVP):**
- Weitere Features, Expansion Strategy, Hiring, etc.

---

### Question Dependencies

Manche Questions hängen voneinander ab:

**Beispiel:**
- Q002 "Local vs Hybrid?" → **MUSS ZUERST** beantwortet werden
- Q006 "Pricing?" → **HÄNGT AB von** Local vs Hybrid (Cloud costs?)

**→ Check dependencies when prioritizing!**

Add "Blocked by" field to question-backlog.md:
```markdown
- [ ] Q006: Freemium vs Paid?
  - **Blocked by:** Q002 (need to know cloud costs)
```

---

## Typische Fehler vermeiden

❌ **Alle Questions auf einmal beantworten**
→ Überwältigend, keine Fokus

✅ **Eine Question pro Iteration**
→ Fokussiert, gute Decisions

---

❌ **Questions ohne Prioritization**
→ Falsche Questions zuerst, blockers später

✅ **RICE Scoring nutzen**
→ Impact-driven prioritization

---

❌ **Questions ohne Research Basis**
→ Bauchgefühl-Entscheidungen

✅ **Jede Question verlinkt zu Base Research**
→ Data-driven decisions

---

## Exit Criteria: Ready for Iterations

- [ ] Base Research complete (alle 6 Kategorien)
- [ ] Questions extracted (10-20 questions)
- [ ] Questions kategorisiert (nach 6 Kategorien)
- [ ] Questions RICE scored
- [ ] question-backlog.md created
- [ ] Top priority question identified
- [ ] Dependencies checked

**→ Ready to start first Iteration!**

---

**Next Step:** Create first iteration file for top priority question

**See:** `planning-framework.md` for GIST iteration process
