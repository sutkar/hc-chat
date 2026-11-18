import duckdb
import pandas as pd

DB_PATH = "../warehouse/hc.duckdb"

# Allow-lists for security and guardrails
ALLOWED_METRICS = {
    "readmission_rate": "AVG(CAST(readmitted AS FLOAT))",
    "total_encounters": "COUNT(*)",
    "avg_length_of_stay": "AVG(length_of_stay_days)",
    "avg_hba1c": "AVG(hba1c_level)"
}

ALLOWED_GROUPS = {
    "age_band": "age_band",
    "insurance_type": "insurance_type",
    "admission_type": "admission_type",
    "primary_dx_group": "primary_dx_group"
}

def get_kpi(metric: str, group_by: str) -> pd.DataFrame:
    """Computes aggregated KPI with small-group suppression (n < 10)."""
    if metric not in ALLOWED_METRICS or group_by not in ALLOWED_GROUPS:
        raise ValueError("Invalid metric or group_by parameter.")
    
    metric_sql = ALLOWED_METRICS[metric]
    group_sql = ALLOWED_GROUPS[group_by]
    
    query = f"""
        SELECT 
            {group_sql} as category,
            {metric_sql} as metric_value,
            COUNT(*) as sample_size
        FROM sv_encounters
        GROUP BY {group_sql}
        HAVING COUNT(*) >= 10
        ORDER BY sample_size DESC
    """
    conn = duckdb.connect(DB_PATH, read_only=True)
    df = conn.execute(query).fetchdf()
    conn.close()
    return df

def drill_down(group_by: str, group_value: str) -> pd.DataFrame:
    """Drills down to individual encounter records for a selected category."""
    if group_by not in ALLOWED_GROUPS:
        raise ValueError("Invalid group_by parameter.")
    
    group_sql = ALLOWED_GROUPS[group_by]
    query = f"""
        SELECT 
            e.encounter_id,
            e.age,
            e.sex,
            e.insurance_type,
            e.primary_dx_group,
            e.length_of_stay_days,
            r.prob_readmit,
            e.readmitted
        FROM sv_encounters e
        LEFT JOIN inference_results r ON e.encounter_id = r.encounter_id
        WHERE {group_sql} = ?
        LIMIT 50
    """
    conn = duckdb.connect(DB_PATH, read_only=True)
    df = conn.execute(query, [group_value]).fetchdf()
    conn.close()
    return df

def get_explanation(encounter_id: int) -> dict:
    """Retrieves predicted readmission probability and top 5 TreeSHAP drivers for a specific encounter ID."""
    conn = duckdb.connect(DB_PATH, read_only=True)
    
    score_res = conn.execute(
        "SELECT prob_readmit FROM inference_results WHERE encounter_id = ?",
        [encounter_id]
    ).fetchone()
    
    shap_res = conn.execute("""
        SELECT feature, feature_value, shap_value, rank 
        FROM inference_shap 
        WHERE encounter_id = ? 
        ORDER BY rank ASC
    """, [encounter_id]).fetchdf()
    
    conn.close()
    
    prob = score_res[0] if score_res else 0.0
    return {
        "encounter_id": encounter_id,
        "prob_readmit": prob,
        "shap_drivers": shap_res.to_dict(orient="records")
    }