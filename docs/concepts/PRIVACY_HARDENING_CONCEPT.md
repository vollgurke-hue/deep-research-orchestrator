# Privacy Hardening - Local Metadata Masking

**Datum:** 2026-01-22
**Quelle:** Gemini Strategic Planning - Hardening Phase
**Status:** Konzept-Definition

---

## 🎯 Kernidee

Bevor ein RLM-Task oder MCTS-Query an ein **Cloud-Modell** (Claude, GPT-4) geht, muss eine **lokale Abstraktions-Schicht** persönliche Daten, Axiome und Identifikatoren entfernen.

**Prinzip:** Die Cloud sieht nur die **Logik-Struktur**, niemals deine Identität oder exakte Finanz-Axiome.

---

## 1. Das Problem: Cloud-APIs & Datenlecks

### Szenario
```python
# Gefährlich: Direkt an Cloud
prompt = f"""
Analyse für mein Startup in Ludwigsstadt:
Budget: 50.000 EUR
Axiome: Datensouveränität, Kein Cloud-Lock-in
Frage: Soll ich Server kaufen oder AWS nutzen?
"""

response = claude_api.query(prompt)
```

**Problem:**
- Anthropic weiß: Dein Standort, Budget, Werte
- Diese Daten landen in Training-Logs
- Potentiell für Werbung/Profilbildung nutzbar

---

## 2. Die Lösung: Abstraktions-Layer

### Konzept: Sanitization Pipeline

```
Original Query → Sanitizer → Abstrahierte Query → Cloud API
                     ↓
              Lokales Mapping
                (privat)

Cloud Response → De-Sanitizer → Original Context → User
```

### Implementierung

```python
class PrivacySanitizer:
    """Entfernt persönliche Informationen vor Cloud-Calls"""

    def __init__(self):
        self.entity_map = {}  # Mapping: Real → Abstract
        self.reverse_map = {}  # Mapping: Abstract → Real

    def sanitize_prompt(self, prompt: str, context: Dict) -> SanitizedPrompt:
        """Abstrahiert einen Prompt für Cloud-Nutzung"""

        sanitized = prompt

        # 1. Geografische Entities
        locations = self._extract_locations(prompt)
        for loc in locations:
            abstract_id = self._get_or_create_id("LOCATION")
            sanitized = sanitized.replace(loc, f"REGION_{abstract_id}")
            self.entity_map[loc] = f"REGION_{abstract_id}"

        # 2. Finanz-Daten
        amounts = self._extract_amounts(prompt)
        for amount in amounts:
            # Runde auf Größenordnung
            magnitude = self._get_magnitude(amount)
            sanitized = sanitized.replace(str(amount), f"BUDGET_{magnitude}")
            self.entity_map[amount] = f"BUDGET_{magnitude}"

        # 3. Axiome (kritisch!)
        if "axiome" in prompt.lower() or "werte" in prompt.lower():
            # Ersetze konkrete Axiome mit Kategorien
            axiom_mapping = {
                "Datensouveränität": "VALUE_PRIVACY",
                "Kein Cloud-Lock-in": "VALUE_INDEPENDENCE",
                "ROI < 10 Jahre": "VALUE_FINANCIAL_PRUDENCE"
            }

            for axiom, abstract in axiom_mapping.items():
                if axiom.lower() in prompt.lower():
                    sanitized = sanitized.replace(axiom, abstract)
                    self.entity_map[axiom] = abstract

        # 4. Persönliche Identifikatoren
        sanitized = re.sub(
            r'\b(mein|meine|ich|wir)\b',
            'THE_USER',
            sanitized,
            flags=re.IGNORECASE
        )

        return SanitizedPrompt(
            original=prompt,
            sanitized=sanitized,
            entity_map=self.entity_map.copy()
        )

    def desanitize_response(
        self,
        response: str,
        entity_map: Dict[str, str]
    ) -> str:
        """Setzt Original-Entities wieder ein"""

        desanitized = response

        # Reverse-Mapping
        for original, abstract in entity_map.items():
            desanitized = desanitized.replace(abstract, original)

        return desanitized

    def _get_magnitude(self, amount: float) -> str:
        """Rundet auf Größenordnung"""
        if amount < 10_000:
            return "LOW"
        elif amount < 100_000:
            return "MEDIUM"
        elif amount < 1_000_000:
            return "HIGH"
        else:
            return "VERY_HIGH"
```

---

## 3. Praktisches Beispiel

### Vor Sanitization

```python
original_prompt = """
Analyse für mein Startup in Ludwigsstadt (Bayern):
Aktuelles Budget: 52.000 EUR
Monatliche Kosten dürfen 800 EUR nicht überschreiten

Meine Axiome:
- Datensouveränität: Daten müssen in Deutschland bleiben
- Kein Cloud-Lock-in: Jederzeit Anbieterwechsel möglich
- ROI < 8 Jahre

Frage: Soll ich eigene Server kaufen (25k EUR) oder AWS nutzen (1.2k EUR/Monat)?
"""
```

### Nach Sanitization

```python
sanitized_prompt = """
Analysis for ENTITY_STARTUP_01 in REGION_A (COUNTRY_B):
Current budget: BUDGET_MEDIUM
Monthly costs must not exceed COST_LOW

Value constraints:
- VALUE_PRIVACY: Data must remain in JURISDICTION_A
- VALUE_INDEPENDENCE: Provider switching must be possible
- VALUE_FINANCIAL_PRUDENCE: Return on investment within TIMEFRAME_SHORT

Question: Should ENTITY_STARTUP_01 purchase hardware (AMOUNT_MEDIUM) or use cloud service (AMOUNT_LOW per month)?
"""

# Lokales Mapping (NIEMALS an Cloud gesendet)
entity_map = {
    "Ludwigsstadt": "REGION_A",
    "Bayern": "REGION_A_STATE",
    "Deutschland": "COUNTRY_B",
    "52000 EUR": "BUDGET_MEDIUM",
    "800 EUR": "COST_LOW",
    "25k EUR": "AMOUNT_MEDIUM",
    "1.2k EUR": "AMOUNT_LOW",
    "Datensouveränität": "VALUE_PRIVACY",
    "Kein Cloud-Lock-in": "VALUE_INDEPENDENCE",
    "ROI < 8 Jahre": "VALUE_FINANCIAL_PRUDENCE"
}
```

### Cloud Response (abstrahiert)

```python
cloud_response = """
For ENTITY_STARTUP_01 with VALUE_PRIVACY and VALUE_INDEPENDENCE constraints:

Option 1 (Hardware):
- Upfront: AMOUNT_MEDIUM
- Monthly: ~COST_VERY_LOW (electricity, maintenance)
- Meets VALUE_PRIVACY: Yes (data in COUNTRY_B)
- Meets VALUE_INDEPENDENCE: Yes (full control)
- ROI: ~7 years

Option 2 (Cloud):
- Upfront: COST_MINIMAL
- Monthly: AMOUNT_LOW
- Meets VALUE_PRIVACY: Depends on provider's COUNTRY_B data center
- Meets VALUE_INDEPENDENCE: Risk of lock-in

Recommendation: Option 1 better aligns with stated values.
"""
```

### De-Sanitized für User

```python
final_response = """
Für dein Startup in Ludwigsstadt mit Datensouveränität und Unabhängigkeits-Anforderungen:

Option 1 (Eigene Hardware):
- Anschaffung: 25.000 EUR
- Monatlich: ~100 EUR (Strom, Wartung)
- Erfüllt Datensouveränität: Ja (Daten in Deutschland)
- Erfüllt Unabhängigkeit: Ja (volle Kontrolle)
- ROI: ~7 Jahre

Option 2 (Cloud):
- Anschaffung: Minimal
- Monatlich: 1.200 EUR
- Erfüllt Datensouveränität: Abhängig von Rechenzentrum in Deutschland
- Erfüllt Unabhängigkeit: Risiko von Lock-in

Empfehlung: Option 1 passt besser zu deinen Werten.
"""
```

---

## 4. Axiom-Schutz: Kritischste Daten

### Problem
Axiome sind deine **intellektuellen Fingerabdrücke**. Sie verraten mehr über dich als Finanz-Daten.

### Lösung: Axiom-Kategorisierung

```python
AXIOM_CATEGORIES = {
    # Finanzielle Axiome
    "roi_threshold": "VALUE_FINANCIAL_PRUDENCE",
    "hidden_costs": "VALUE_TRANSPARENCY",
    "opportunity_cost": "VALUE_OPTIMIZATION",

    # Souveränitäts-Axiome
    "data_sovereignty": "VALUE_PRIVACY",
    "no_cloud_dependency": "VALUE_INDEPENDENCE",
    "vendor_independence": "VALUE_FREEDOM",

    # Qualitäts-Axiome
    "source_reliability": "VALUE_QUALITY",
    "fact_verification": "VALUE_ACCURACY",
    "empirical_evidence": "VALUE_RATIONALITY"
}

def sanitize_axiom(axiom_id: str) -> str:
    """Konvertiere konkretes Axiom zu generischer Kategorie"""
    return AXIOM_CATEGORIES.get(axiom_id, "VALUE_GENERAL")
```

### Axiom-Evaluation LOKAL halten

```python
# RICHTIG: Lokales Modell für Axiom-Prüfung
axiom_judge = AxiomJudge(
    axioms=load_local_axioms(),
    llm=local_abliterated_model  # Llama-3-70B lokal
)

# Cloud nur für neutrale Fakten-Extraktion
cloud_spo = cloud_api.extract_spo(sanitized_text)

# Axiom-Bewertung LOKAL
local_score = axiom_judge.evaluate(cloud_spo)
```

---

## 5. Differential Privacy für Zahlen

### Konzept: Noise Injection

```python
def add_differential_privacy(value: float, epsilon: float = 1.0) -> float:
    """Fügt Laplace-Noise hinzu für Differential Privacy"""

    # Laplace-Mechanismus
    scale = 1.0 / epsilon
    noise = np.random.laplace(0, scale)

    return value + noise

# Beispiel
original_budget = 52_000
sanitized_budget = add_differential_privacy(52_000, epsilon=0.5)
# → z.B. 51_743 oder 52_389

# An Cloud senden: "Budget ~52k EUR"
```

### Wann nutzen?

```python
class PrivacyConfig:
    """Konfiguration für Privacy-Level"""

    # Level 1: Keine Cloud (alles lokal)
    PARANOID = {
        "use_cloud": False,
        "local_only": True
    }

    # Level 2: Cloud mit starker Anonymisierung
    STRICT = {
        "use_cloud": True,
        "sanitize_entities": True,
        "sanitize_axioms": True,
        "add_noise": True,
        "epsilon": 0.5
    }

    # Level 3: Cloud mit leichter Anonymisierung
    MODERATE = {
        "use_cloud": True,
        "sanitize_entities": True,
        "sanitize_axioms": True,
        "add_noise": False
    }

    # Level 4: Keine Anonymisierung (vertraue Cloud)
    PERMISSIVE = {
        "use_cloud": True,
        "sanitize_entities": False,
        "sanitize_axioms": False
    }
```

---

## 6. Two-Tier Architecture: Local + Cloud

### CEO (Cloud) + Worker (Local) Strategie

```python
class HybridLLMOrchestrator:
    """Kombiniert lokale und Cloud-Modelle privacy-aware"""

    def __init__(self, privacy_config: Dict):
        self.local_llm = LocalLLM("llama-3-70b")
        self.cloud_llm = CloudLLM("claude-opus-4")
        self.sanitizer = PrivacySanitizer()
        self.config = privacy_config

    def query(self, prompt: str, task_type: str) -> str:
        """Intelligente Routing basierend auf Privacy"""

        # Entscheide: Lokal oder Cloud?
        if self._is_sensitive(prompt, task_type):
            # Sensitive Tasks → Lokal
            return self.local_llm.query(prompt)

        else:
            # Nicht-sensitive Tasks → Cloud (mit Sanitization)
            sanitized = self.sanitizer.sanitize_prompt(prompt)
            cloud_response = self.cloud_llm.query(sanitized.sanitized)
            return self.sanitizer.desanitize_response(
                cloud_response,
                sanitized.entity_map
            )

    def _is_sensitive(self, prompt: str, task_type: str) -> bool:
        """Bestimme ob Task sensitive Daten enthält"""

        # Immer lokal
        if task_type in ["axiom_evaluation", "financial_calculation"]:
            return True

        # Checke Keywords
        sensitive_keywords = [
            "axiom", "werte", "budget", "standort",
            "persönlich", "firma", "kunde"
        ]

        if any(kw in prompt.lower() for kw in sensitive_keywords):
            return True

        return False
```

---

## 7. Audit-Log: Transparenz

### Jeder Cloud-Call wird geloggt

```python
@dataclass
class CloudCallLog:
    """Log-Eintrag für Cloud-API Calls"""

    timestamp: datetime
    prompt_hash: str  # SHA256 vom Original-Prompt
    sanitized_prompt: str  # Was an Cloud ging
    entity_map_size: int  # Wie viele Entities ersetzt
    response_hash: str
    model_used: str  # claude-opus-4, gpt-4, etc.
    tokens_used: int
    cost_usd: float

class CloudAuditLogger:
    """Loggt alle Cloud-Interaktionen"""

    def log_call(
        self,
        original_prompt: str,
        sanitized_prompt: str,
        entity_map: Dict,
        response: str,
        metadata: Dict
    ):
        """Logge Cloud-Call für späteres Audit"""

        log_entry = CloudCallLog(
            timestamp=datetime.now(),
            prompt_hash=hashlib.sha256(original_prompt.encode()).hexdigest(),
            sanitized_prompt=sanitized_prompt,
            entity_map_size=len(entity_map),
            response_hash=hashlib.sha256(response.encode()).hexdigest(),
            model_used=metadata["model"],
            tokens_used=metadata["tokens"],
            cost_usd=metadata["cost"]
        )

        # Persistiere
        self.save_to_db(log_entry)

        # Monthly Report
        if self.should_send_report():
            self.generate_privacy_report()

def generate_privacy_report(self) -> str:
    """Erstelle monatlichen Privacy-Report"""

    logs = self.get_logs_last_month()

    report = f"""
    === PRIVACY AUDIT REPORT ===
    Zeitraum: {self.start_date} - {self.end_date}

    Cloud-Calls: {len(logs)}
    Entities sanitisiert: {sum(l.entity_map_size for l in logs)}
    Kosten: ${sum(l.cost_usd for l in logs):.2f}

    Häufigste sanitisierte Entities:
    {self._top_sanitized_entities(logs)}

    Empfehlung:
    {self._generate_recommendations(logs)}
    """

    return report
```

---

## 8. Attack Scenarios & Defenses

### Angriff 1: Re-Identification via Kombination

**Problem:**
```
Call 1: "ENTITY_A in REGION_B with BUDGET_MEDIUM"
Call 2: "ENTITY_A evaluating PRODUCT_X"
Call 3: "ENTITY_A has constraint VALUE_PRIVACY"

→ Cloud könnte über Calls hinweg Profil erstellen
```

**Defense: Session Randomization**
```python
# Verschiedene Calls nutzen verschiedene IDs
session_1 = Sanitizer(session_id="random_1")
session_2 = Sanitizer(session_id="random_2")

# ENTITY_A wird zu ENTITY_17 in Session 1
# ENTITY_A wird zu ENTITY_42 in Session 2
```

### Angriff 2: Timing-Analyse

**Problem:**
Timing zwischen Calls könnte User-Patterns verraten.

**Defense: Request Batching & Delay**
```python
# Füge Random-Delay hinzu
time.sleep(np.random.uniform(1, 10))

# Batch mehrere Requests
batch_requests([req1, req2, req3], randomize_order=True)
```

---

## 9. Implementation Checklist

### Phase 1: Basic Sanitization
```
□ PrivacySanitizer Class
□ Entity Extraction (Locations, Amounts, Names)
□ Abstraction-Mapping
□ De-Sanitization
```

### Phase 2: Axiom Protection
```
□ Axiom-Kategorisierung
□ Lokales Axiom-Evaluation (kein Cloud)
□ Differential Privacy für Zahlen
```

### Phase 3: Hybrid Architecture
```
□ HybridLLMOrchestrator
□ Sensitivity Detection
□ Automatic Routing (Local vs Cloud)
```

### Phase 4: Audit & Compliance
```
□ CloudAuditLogger
□ Privacy Reports
□ Attack Defense Mechanisms
```

---

## 10. Compliance & Rechtliches

### GDPR-Konformität

```python
# GDPR Article 25: Data Protection by Design
class GDPRCompliantSanitizer(PrivacySanitizer):
    """GDPR-konformer Sanitizer"""

    def __init__(self):
        super().__init__()
        self.data_minimization = True  # Nur nötige Daten
        self.purpose_limitation = True  # Zweckbindung

    def sanitize_for_cloud(self, prompt: str, purpose: str):
        """Sanitisiere mit GDPR-Prinzipien"""

        # 1. Data Minimization
        # Entferne ALLE nicht-essentiellen persönlichen Daten
        minimal_prompt = self._minimize_data(prompt, purpose)

        # 2. Purpose Limitation
        # Tag: Wofür wird dieser Call genutzt?
        tagged_prompt = f"[PURPOSE: {purpose}]\n{minimal_prompt}"

        # 3. Standard Sanitization
        return super().sanitize_prompt(tagged_prompt)
```

---

## Referenzen
- Differential Privacy - Dwork & Roth 2014
- GDPR Article 25 - Data Protection by Design
- De-identification Best Practices - NIST 2015
- Gemini Strategic Planning Session (Jan 2026)
