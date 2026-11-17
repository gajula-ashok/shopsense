import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import numpy as np

# Use an isolated tracking directory within the project
MLFLOW_TRACKING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mlflow_data")
os.makedirs(MLFLOW_TRACKING_DIR, exist_ok=True)
REGISTRY_FILE = os.path.join(MLFLOW_TRACKING_DIR, "model_registry.json")

def _load_registry() -> Dict[str, Any]:
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_registry(registry: Dict[str, Any]):
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, default=str)

def log_and_register_model(
    model_name: str,
    params: Dict[str, Any],
    metrics: Dict[str, Any],
    status: str = "PRODUCTION",
    artifacts: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Tracks model parameters, metrics, dates, and versioning.
    Registers model in the local registry with full version history.
    """
    registry = _load_registry()

    if model_name not in registry:
        registry[model_name] = {
            "model_name": model_name,
            "versions": [],
            "current_production_version": 1
        }

    version_number = len(registry[model_name]["versions"]) + 1

    entry = {
        "version": version_number,
        "logged_at": datetime.now().isoformat(),
        "status": status,
        "parameters": params,
        "metrics": metrics,
        "artifacts_path": artifacts.get("path") if artifacts else None
    }

    registry[model_name]["versions"].append(entry)
    registry[model_name]["latest_version"] = version_number
    if status == "PRODUCTION":
        registry[model_name]["current_production_version"] = version_number

    _save_registry(registry)
    return entry

def get_registered_models() -> List[Dict[str, Any]]:
    registry = _load_registry()
    result = []
    for m_name, data in registry.items():
        versions = data.get("versions", [])
        latest = versions[-1] if versions else {}
        result.append({
            "model_name": m_name,
            "total_versions": len(versions),
            "current_production_version": data.get("current_production_version", 1),
            "latest_version": latest.get("version", 1),
            "last_training_date": latest.get("logged_at", "N/A"),
            "status": latest.get("status", "ACTIVE"),
            "latest_metrics": latest.get("metrics", {}),
            "latest_parameters": latest.get("parameters", {})
        })
    return result

def get_model_history(model_name: str) -> List[Dict[str, Any]]:
    registry = _load_registry()
    if model_name in registry:
        return registry[model_name].get("versions", [])
    return []
