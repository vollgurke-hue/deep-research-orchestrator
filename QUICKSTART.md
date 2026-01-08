# Quick Start - Deep Research Orchestrator

## 🚀 System Starten (in 30 Sekunden)

```bash
./start_dev.sh
```

Das war's! Öffne jetzt: **http://localhost:5173**

## 📋 Was läuft wo?

| Service | Port | URL |
|---------|------|-----|
| **Vue Frontend** | 5173 | http://localhost:5173 |
| **API Server** | 5000 | http://localhost:5000/api/status |
| ~~Alte GUI~~ | ~~8002~~ | ❌ **VERALTET - NICHT NUTZEN** |

## 🎯 Research Creator nutzen

1. Öffne http://localhost:5173
2. Klicke auf **"Research Creator"** in der Navigation
3. Gib deine Forschungsbeschreibung ein
4. Der Mock Mode gibt sofort Ergebnisse zurück!

### Beispiel (aus QUICK_TEST.md):

```
Beschreibung:
Ich möchte ein SaaS-Produkt für AI-gestütztes Tutoring im Bildungsbereich validieren.
Das Produkt soll Schülern und Studenten personalisierte Lernhilfe bieten, automatisch
Schwachstellen erkennen und adaptive Übungen generieren.

Ziel:
Umfassende Marktanalyse, Wettbewerbsanalyse, technische Machbarkeit und
Geschäftsmodell-Validierung.
```

## ✅ Mock Mode vs Real Mode

### Mock Mode (AKTIV - Standard)
- ⚡ Sofortige Antworten
- 💪 Funktioniert auf schwacher Hardware
- 🎯 Perfekt zum Testen des Workflows
- ❌ Keine echten LLM-Aufrufe

### Real Mode (Für Produktion)
Erst wenn du bessere Hardware hast:

1. Öffne `api_server.py`
2. Ändere Zeile 44 und 75:
   ```python
   # Von:
   helper = ResearchQualityHelper(use_mock=True)
   generator = ResearchGenerator(use_mock=True)

   # Zu:
   helper = ResearchQualityHelper(use_mock=False)
   generator = ResearchGenerator(use_mock=False)
   ```
3. Stelle sicher llama-server läuft auf Port 8081

## 🛑 System Stoppen

```bash
# CTRL+C im Terminal wo start_dev.sh läuft

# Oder manuell:
pkill -f api_server.py
pkill -f "npm run dev"
```

## 🔧 Troubleshooting

### Port 8002 läuft noch?
```bash
fuser -k 8002/tcp
pkill -9 -f "serve_gui"
```

### Vue lädt nicht?
```bash
cd gui
npm install
cd ..
./start_dev.sh
```

### API antwortet nicht?
```bash
tail -f /tmp/api_server.log
```

## 📚 Mehr Infos

- **Vollständige Architektur**: Siehe `ARCHITECTURE.md`
- **Mock Mode Details**: Siehe `MOCK_MODE_GUIDE.md`
- **Clean Architecture**: Siehe `CLEAN_ARCHITECTURE.md`

## 🎊 Das war's!

Dein System ist jetzt ready. Viel Spaß beim Testen! 🚀

---

## 🔧 Recent Fixes (2026-01-04)

### Dashboard Now Shows Real Data
- ✅ 1 Framework loaded from config
- ✅ 9 Workflows loaded from config
- ✅ 7 Techniques loaded from config

### Docs Viewer Working
- ✅ All documentation files load correctly
- ✅ Markdown content displays properly
- ✅ Categorized into Guides/Architecture/Frameworks

---

**Erstellt:** 2026-01-04
**Last Updated:** 2026-01-04 16:30
**Status:** READY FOR TESTING ✅
**Mock Mode:** AKTIV ✅
