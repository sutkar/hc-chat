### C. `hc-chat/README.md`
```markdown
# hc-chat: Streamlit UI & Safe Chat Assistant

## Purpose
Provides the user-facing Streamlit dashboard, interactive KPI drill-down explorers, visual TreeSHAP risk factor charts, and a guardrail-protected chat interface[cite: 1, 4].

## Setup & Installation (Windows PowerShell)
1. Open PowerShell and navigate to `hc-chat`.
2. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
3. 3-Minute Demo Walkthrough Script below-

1. **Introduction & Safety Check (0:00 - 0:30):**
   * Open the Streamlit app (`streamlit run app.py`).
   * Point out the prominent red warning banner: **`⚠️ DEMO ONLY — NOT FOR CLINICAL USE`**[cite: 1].
2. **Data Governance & dbt Verification (0:30 - 1:00):**
   * Show terminal output of `dbt build --profiles-dir .` passing cleanly with 0 failures across all staging models and schema tests.
3. **KPI Explorer & Cohort Drill-Down (1:00 - 1:45):**
   * Select *Readmission Rate* grouped by *Insurance Type*.
   * View the Plotly bar chart with small-group suppression ($n < 10$)[cite: 1].
   * Click **Load Encounter Records** to inspect individual anonymized patient rows[cite: 1].
4. **Explainable AI / TreeSHAP (1:45 - 2:30):**
   * Navigate to the **Encounter Risk & SHAP Explainability** tab.
   * Input Encounter ID `42` to display the predicted readmission probability and its localized TreeSHAP feature impact chart[cite: 1].
5. **Secure Chat Assistant & Guardrail Demonstration (2:30 - 3:00):**
   * Type a natural language query in the chat assistant (*"What is the readmission rate by age group?"*)[cite: 1].
   * Explain how prompts are safely routed through allow-listed parameterized functions rather than direct SQL execution[cite: 1].