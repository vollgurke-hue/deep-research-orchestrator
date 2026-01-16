# Quick Test - Response Collection Workflow

## Test-Text für Research Creator

**Kopiere diesen Text in Step 0:**

```
Ich möchte ein SaaS-Produkt für AI-gestütztes Tutoring im Bildungsbereich validieren.
Das Produkt soll Schülern und Studenten personalisierte Lernhilfe bieten, automatisch
Schwachstellen erkennen und adaptive Übungen generieren. Zielgruppe sind zunächst
deutsche Gymnasien und Universitäten. Ich brauche eine umfassende Marktanalyse,
Wettbewerbsanalyse, technische Machbarkeit und Geschäftsmodell-Validierung.
```

---

## Vollständiger Test-Flow (5-10 Minuten)

### 1. Starte Backend + Frontend

**Terminal 1 (Backend):**
```bash
cd /home/phili/Schreibtisch/AI_Projects/deep-research-orchestrator
python viewer/serve_gui.py
```
→ Läuft auf http://localhost:8002

**Terminal 2 (Frontend):**
```bash
cd /home/phili/Schreibtisch/AI_Projects/deep-research-orchestrator/gui
npm run dev
```
→ Läuft auf http://localhost:5174

---

### 2. Öffne Research Creator

```
URL: http://localhost:5174/research/create
```

---

### 3. Workflow durchgehen

#### **Step 0: Describe Research**
- Paste den Test-Text oben
- Klick: **Generate Structure →**
- ⏳ Warte ~10 Sekunden

#### **Step 1: Select Themes**
- System zeigt ~12-15 hierarchische Themen
- Wähle 3-5 Themen aus (z.B.):
  - ✅ Marktanalyse & Zielgruppe
  - ✅ Wettbewerbsanalyse
  - ✅ Technische Machbarkeit
  - ✅ Geschäftsmodell & Monetarisierung
- Klick: **Continue →**

#### **Step 2: Blindspot Detection** (Optional)
- Klick: **Skip Blindspot Detection →**
- (Oder teste mit "Detect Blindspots" - dauert ~15 Sek)

#### **Step 3: Generate Deep Prompts**
- Klick: **Generate Deep Research Prompts →**
- ⏳ Warte ~20 Sekunden
- System generiert 3-5 detaillierte Prompts

#### **Step 4: 🆕 Response Collection** ← NEUER STEP!

**Jetzt der wichtige Teil:**

1. **Prompt 1 angezeigt** (z.B. "Marktanalyse")

2. **Klick: [📋 Copy Full Prompt]**
   → Prompt ist in Zwischenablage

3. **Gehe zu Claude.ai / ChatGPT / Gemini**
   → Paste den Prompt
   → Warte auf Antwort

4. **Kopiere die Antwort**

5. **Zurück zum System:**
   - Model wählen: `[Claude Opus ▼]`
   - Paste Response: [Antwort einfügen]
   - Klick: **[Add & Evaluate →]**

6. **System evaluiert sofort:**
   ```
   ✅ Claude Opus
      Relevance: 92% | Accuracy: 88%

   🟢 Quality threshold met!
   💡 You can proceed now or add more models (up to 2 more).
   ```

7. **Entscheidung:**
   - **A)** Quality gut → Klick **Continue to Synthesis →**
   - **B)** Noch ein Modell testen → Wiederhole 3-6 mit GPT-4

8. **Für alle Prompts wiederholen**
   - Navigation: **[Next Prompt →]**
   - Mindestens 1 Response pro Prompt nötig

#### **Step 5: Success & Summary**
- Zeigt Statistiken:
  - Total Responses: 5
  - Average Quality: 90%
- Anleitung für Multi-AI Synthesis

---

## Mock-Test ohne externe Models

**Wenn du NICHT zu Claude/GPT gehen willst:**

Verwende diese Mock-Antworten:

### Mock Response 1 (Marktanalyse):
```
Der deutsche EdTech-Markt wächst mit 15% CAGR. Haupttreiber sind:
- Digitalisierungsoffensive an Schulen (DigitalPakt 2.0)
- Steigende Nachfrage nach personalisiertem Lernen
- COVID-19 hat Online-Learning etabliert

Zielgruppe Gymnasien: 3.200 Schulen in Deutschland, ~2,5 Mio Schüler
Universitäten: 420 Hochschulen, ~2,9 Mio Studenten

Zahlungsbereitschaft:
- Schulen: €5-10 pro Schüler/Monat (über Schulbudget)
- Studenten: €15-25/Monat (direktes Abo)

Marktpotenzial: €450M/Jahr (bei 10% Penetration)
```

### Mock Response 2 (Wettbewerb):
```
Hauptkonkurrenten im deutschen Markt:

1. simpleclub (€30M Funding)
   - Stärke: Video-Content, starke Brand
   - Schwäche: Wenig Personalisierung

2. StudySmarter (€15M Funding)
   - Stärke: Lernkarten, Community
   - Schwäche: Keine AI-Tutoring

3. Sofatutor (etabliert seit 2009)
   - Stärke: Großer Content-Katalog
   - Schwäche: Veraltete Technologie

Gap im Markt: Echtes AI-gestütztes adaptives Tutoring
```

---

## Was du sehen solltest

### Response Collection View:

```
┌─────────────────────────────────────────┐
│ Prompt 1 of 3: Marktanalyse           │
│                                         │
│ [📋 Copy Full Prompt]                  │
│                                         │
│ Responses: 1 / max 3                   │
│                                         │
│ ✅ Claude Opus                         │
│    Relevance: 92% | Accuracy: 88%     │
│                                         │
│ 🟢 Quality threshold met!              │
│                                         │
│ Overall Progress: [████░░] 1/3         │
│                                         │
│ [← Previous] [Continue to Synthesis →] │
└─────────────────────────────────────────┘
```

---

## Troubleshooting

### Backend nicht erreichbar?
```bash
# Check ob Backend läuft
curl http://localhost:8002/api/status

# Falls nicht → neu starten
python viewer/serve_gui.py
```

### Frontend zeigt Fehler?
```bash
# Check Browser Console (F12)
# Common issue: CORS → sollte aber nicht sein

# Restart Frontend
cd gui
npm run dev
```

### Evaluation zeigt immer gleiche Scores?
→ Das ist NORMAL! Mock-Mode ist aktiv.

In `src/services/response_evaluator.py:33`:
```python
USE_MOCK = True  # ← Für Testing
```

Mock gibt immer Random zwischen 75-95%.

---

## Erwartete Test-Dauer

- **Minimal-Test**: 2 Minuten (1 Prompt, 1 Response mit Mock-Text)
- **Vollständiger Test**: 5 Minuten (3 Prompts, je 1 Response)
- **Umfassend**: 10 Minuten (3 Prompts, je 2-3 Responses von echten Models)

---

## Nächste Schritte nach erfolgreichem Test

1. **Mock → Real LLM**
   - Set `USE_MOCK = False`
   - Evaluation nutzt dann echtes lokales Modell

2. **Persistence**
   - Sessions in JSON/DB speichern
   - Später fortsetzen

3. **Multi-AI Synthesis**
   - Alle Responses aggregieren
   - Final Report generieren

---

**Viel Erfolg beim Testen! 🚀**
