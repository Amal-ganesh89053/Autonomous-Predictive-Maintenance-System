"""Telemetry tools for accessing vehicle sensor data (6-sensor ML dataset)."""
import json
from pathlib import Path
from typing import Optional

# Path to data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# ──────────────────────────────────────────────────────────────────────────────
# Normal operating thresholds derived from the dataset domain knowledge
# ──────────────────────────────────────────────────────────────────────────────
THRESHOLDS = {
    # RPM: typical idle 400–800, running 600–1800; below 300 or extreme spikes are anomalies
    "engine_rpm":        {"low": 300.0,  "high": 2000.0},
    # Lubricating oil pressure (bar / normalised units)
    "lub_oil_pressure":  {"low": 2.5,    "high": 6.0,   "critical_low": 1.5},
    # Fuel line pressure
    "fuel_pressure":     {"low": 3.5,    "high": 9.0,   "critical_high": 11.0},
    # Coolant system pressure
    "coolant_pressure":  {"low": 1.5,    "high": 3.5,   "critical_low": 1.0},
    # Lubricating oil temperature (°C)
    "lub_oil_temp":      {"low": 60.0,   "high": 85.0,  "critical_high": 95.0},
    # Engine coolant temperature (°C)
    "coolant_temp":      {"low": 60.0,   "high": 85.0,  "critical_high": 95.0},
}


def get_vehicle_telemetry(vehicle_id: str) -> dict:
    """
    Retrieves the current real-time telemetry data for a specific vehicle.

    The telemetry is based on 6 engine sensors:
      - engine_rpm       : Engine speed (RPM)
      - lub_oil_pressure : Lubricating oil pressure
      - fuel_pressure    : Fuel line pressure
      - coolant_pressure : Coolant system pressure
      - lub_oil_temp     : Lubricating oil temperature (°C)
      - coolant_temp     : Engine coolant temperature (°C)
      - label            : ML fault label (0 = normal, 1 = fault)

    Args:
        vehicle_id: The unique identifier of the vehicle (e.g., 'VH001')

    Returns:
        dict: Current telemetry data with exactly 7 fields: 6 sensor readings +
              'label' (0=normal, 1=fault). Returns error dict if vehicle not found.
    """
    try:
        with open(DATA_DIR / "telemetry_stream.json", "r") as f:
            telemetry_data = json.load(f)

        if vehicle_id in telemetry_data:
            return {
                "status": "success",
                "data": telemetry_data[vehicle_id]
            }
        else:
            return {
                "status": "error",
                "error_message": f"No telemetry data found for vehicle {vehicle_id}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve telemetry: {str(e)}"
        }


def get_sensor_history(vehicle_id: str, sensor_type: str, days: int = 7) -> dict:
    """
    Retrieves historical sensor readings for a specific sensor over a time period.

    Supported sensor_type values (matching the 6-sensor dataset):
      engine_rpm, lub_oil_pressure, fuel_pressure,
      coolant_pressure, lub_oil_temp, coolant_temp

    Args:
        vehicle_id:  The unique identifier of the vehicle
        sensor_type: One of the 6 sensor field names
        days:        Number of days of history to retrieve (default: 7)

    Returns:
        dict: Historical readings with timestamps and trend analysis
    """
    # Simulated 7-day histories per sensor per vehicle (representative values)
    sensor_histories: dict = {
        "engine_rpm": {
            "VH001": [870, 865, 860, 858, 856, 857, 856],
            "VH004": [395, 390, 385, 382, 380, 379, 379],
            "VH010": [1450, 1440, 1435, 1430, 1428, 1427, 1427],
        },
        "lub_oil_pressure": {
            "VH001": [4.10, 4.08, 4.07, 4.06, 4.05, 4.04, 4.04],
            "VH007": [2.10, 2.07, 2.05, 2.04, 2.03, 2.02, 2.02],
            "VH002": [2.65, 2.63, 2.62, 2.61, 2.61, 2.61, 2.61],
        },
        "fuel_pressure": {
            "VH002": [9.80, 9.90, 10.10, 10.20, 10.35, 10.45, 10.45],
            "VH004": [4.80, 4.78, 4.75, 4.73, 4.72, 4.71, 4.71],
            "VH007": [7.00, 7.05, 7.08, 7.10, 7.12, 7.13, 7.13],
        },
        "coolant_pressure": {
            "VH009": [3.10, 3.12, 3.15, 3.17, 3.18, 3.19, 3.19],
            "VH003": [1.90, 1.88, 1.87, 1.87, 1.87, 1.87, 1.87],
            "VH005": [1.95, 1.94, 1.93, 1.92, 1.91, 1.91, 1.91],
        },
        "lub_oil_temp": {
            "VH003": [79.5, 80.1, 80.8, 81.2, 81.5, 81.7, 81.84],
            "VH001": [73.5, 73.6, 73.7, 73.8, 73.8, 73.9, 73.86],
            "VH006": [77.5, 77.6, 77.7, 77.8, 77.9, 77.9, 77.92],
        },
        "coolant_temp": {
            "VH006": [80.5, 80.9, 81.3, 81.7, 82.0, 82.2, 82.37],
            "VH001": [71.0, 71.0, 71.0, 71.0, 71.0, 71.0, 71.05],
            "VH002": [78.5, 78.8, 79.0, 79.1, 79.2, 79.2, 79.25],
        },
    }

    try:
        valid_sensors = list(THRESHOLDS.keys())
        if sensor_type not in valid_sensors:
            return {
                "status": "error",
                "error_message": (
                    f"Unknown sensor type: '{sensor_type}'. "
                    f"Valid options: {valid_sensors}"
                )
            }

        history = sensor_histories.get(sensor_type, {}).get(
            vehicle_id,
            [None] * days  # No specific history available
        )

        # Remove None and compute trend
        valid_readings = [v for v in history if v is not None]
        if len(valid_readings) >= 2:
            trend = (
                "increasing" if valid_readings[-1] > valid_readings[0] else
                "decreasing" if valid_readings[-1] < valid_readings[0] else
                "stable"
            )
            change_percent = (
                ((valid_readings[-1] - valid_readings[0]) / valid_readings[0]) * 100
                if valid_readings[0] != 0 else 0
            )
        else:
            trend = "stable"
            change_percent = 0

        return {
            "status": "success",
            "vehicle_id": vehicle_id,
            "sensor_type": sensor_type,
            "readings": history[-days:],
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "period_days": days
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve sensor history: {str(e)}"
        }


def detect_anomalies(vehicle_id: str) -> dict:
    """
    Runs anomaly detection on all 6 sensor readings for a vehicle against
    established operating thresholds. Returns a list of detected anomalies
    with severity and recommendations, plus the overall fault status.

    Anomaly logic mirrors the ML label (0 = normal, 1 = fault):
      - Sensor values outside safe ranges trigger warnings or critical alerts.
      - The ML 'label' field (0/1) is the ground-truth fault indicator.

    Args:
        vehicle_id: The unique identifier of the vehicle

    Returns:
        dict: Detected anomalies with severity levels and recommended actions,
              overall status (normal / warning / critical), and ML label.
    """
    try:
        with open(DATA_DIR / "telemetry_stream.json", "r") as f:
            telemetry_data = json.load(f)

        if vehicle_id not in telemetry_data:
            return {
                "status": "error",
                "error_message": f"No telemetry data found for vehicle {vehicle_id}"
            }

        vd = telemetry_data[vehicle_id]
        anomalies = []

        # ── Engine RPM ───────────────────────────────────────────────────────
        rpm = vd.get("engine_rpm", 800)
        if rpm < THRESHOLDS["engine_rpm"]["low"]:
            anomalies.append({
                "sensor": "engine_rpm",
                "issue": "rpm_critically_low",
                "severity": "critical",
                "current_value": rpm,
                "threshold": THRESHOLDS["engine_rpm"]["low"],
                "recommendation": "Engine may be misfiring or stalling. Inspect immediately."
            })
        elif rpm > THRESHOLDS["engine_rpm"]["high"]:
            anomalies.append({
                "sensor": "engine_rpm",
                "issue": "rpm_abnormally_high",
                "severity": "warning",
                "current_value": rpm,
                "threshold": THRESHOLDS["engine_rpm"]["high"],
                "recommendation": "Possible governor or throttle issue. Schedule inspection."
            })

        # ── Lubricating Oil Pressure ─────────────────────────────────────────
        lop = vd.get("lub_oil_pressure", 4.0)
        if lop < THRESHOLDS["lub_oil_pressure"]["critical_low"]:
            anomalies.append({
                "sensor": "lub_oil_pressure",
                "issue": "lub_oil_pressure_critical_low",
                "severity": "critical",
                "current_value": lop,
                "threshold": THRESHOLDS["lub_oil_pressure"]["critical_low"],
                "recommendation": "Stop engine immediately. Risk of severe engine damage."
            })
        elif lop < THRESHOLDS["lub_oil_pressure"]["low"]:
            anomalies.append({
                "sensor": "lub_oil_pressure",
                "issue": "lub_oil_pressure_low",
                "severity": "warning",
                "current_value": lop,
                "threshold": THRESHOLDS["lub_oil_pressure"]["low"],
                "recommendation": "Check oil level and pump. Schedule service within 24 hours."
            })

        # ── Fuel Pressure ────────────────────────────────────────────────────
        fp = vd.get("fuel_pressure", 5.0)
        if fp > THRESHOLDS["fuel_pressure"]["critical_high"]:
            anomalies.append({
                "sensor": "fuel_pressure",
                "issue": "fuel_pressure_critical_high",
                "severity": "critical",
                "current_value": fp,
                "threshold": THRESHOLDS["fuel_pressure"]["critical_high"],
                "recommendation": "Fuel system overpressure. Risk of fuel line failure. Stop engine."
            })
        elif fp > THRESHOLDS["fuel_pressure"]["high"]:
            anomalies.append({
                "sensor": "fuel_pressure",
                "issue": "fuel_pressure_high",
                "severity": "warning",
                "current_value": fp,
                "threshold": THRESHOLDS["fuel_pressure"]["high"],
                "recommendation": "Inspect fuel pressure regulator. Schedule service."
            })
        elif fp < THRESHOLDS["fuel_pressure"]["low"]:
            anomalies.append({
                "sensor": "fuel_pressure",
                "issue": "fuel_pressure_low",
                "severity": "warning",
                "current_value": fp,
                "threshold": THRESHOLDS["fuel_pressure"]["low"],
                "recommendation": "Check fuel pump and filter. Engine performance may degrade."
            })

        # ── Coolant Pressure ─────────────────────────────────────────────────
        cp = vd.get("coolant_pressure", 2.0)
        if cp < THRESHOLDS["coolant_pressure"]["critical_low"]:
            anomalies.append({
                "sensor": "coolant_pressure",
                "issue": "coolant_pressure_critical_low",
                "severity": "critical",
                "current_value": cp,
                "threshold": THRESHOLDS["coolant_pressure"]["critical_low"],
                "recommendation": "Possible coolant leak or pump failure. Stop engine immediately."
            })
        elif cp < THRESHOLDS["coolant_pressure"]["low"]:
            anomalies.append({
                "sensor": "coolant_pressure",
                "issue": "coolant_pressure_low",
                "severity": "warning",
                "current_value": cp,
                "threshold": THRESHOLDS["coolant_pressure"]["low"],
                "recommendation": "Inspect coolant system for leaks. Schedule service."
            })
        elif cp > THRESHOLDS["coolant_pressure"]["high"]:
            anomalies.append({
                "sensor": "coolant_pressure",
                "issue": "coolant_pressure_high",
                "severity": "warning",
                "current_value": cp,
                "threshold": THRESHOLDS["coolant_pressure"]["high"],
                "recommendation": "Inspect coolant pressure cap and expansion tank."
            })

        # ── Lubricating Oil Temperature ──────────────────────────────────────
        lot = vd.get("lub_oil_temp", 75.0)
        if lot > THRESHOLDS["lub_oil_temp"]["critical_high"]:
            anomalies.append({
                "sensor": "lub_oil_temp",
                "issue": "lub_oil_temp_critical_high",
                "severity": "critical",
                "current_value": lot,
                "threshold": THRESHOLDS["lub_oil_temp"]["critical_high"],
                "recommendation": "Oil overheating. Stop engine. Check oil cooler and level."
            })
        elif lot > THRESHOLDS["lub_oil_temp"]["high"]:
            anomalies.append({
                "sensor": "lub_oil_temp",
                "issue": "lub_oil_temp_high",
                "severity": "warning",
                "current_value": lot,
                "threshold": THRESHOLDS["lub_oil_temp"]["high"],
                "recommendation": "Oil running hot. Check oil cooler and coolant system."
            })

        # ── Coolant Temperature ──────────────────────────────────────────────
        ct = vd.get("coolant_temp", 75.0)
        if ct > THRESHOLDS["coolant_temp"]["critical_high"]:
            anomalies.append({
                "sensor": "coolant_temp",
                "issue": "coolant_temp_critical_high",
                "severity": "critical",
                "current_value": ct,
                "threshold": THRESHOLDS["coolant_temp"]["critical_high"],
                "recommendation": "Engine overheating. Stop vehicle immediately."
            })
        elif ct > THRESHOLDS["coolant_temp"]["high"]:
            anomalies.append({
                "sensor": "coolant_temp",
                "issue": "coolant_temp_high",
                "severity": "warning",
                "current_value": ct,
                "threshold": THRESHOLDS["coolant_temp"]["high"],
                "recommendation": "Monitor cooling system. Check coolant level and radiator."
            })

        # ── ML label cross-check ─────────────────────────────────────────────
        ml_label = vd.get("label", 0)
        if ml_label == 1 and not anomalies:
            # ML model flags fault but no threshold exceeded — soft anomaly
            anomalies.append({
                "sensor": "ml_model",
                "issue": "ml_fault_detected",
                "severity": "warning",
                "current_value": ml_label,
                "threshold": 0,
                "recommendation": (
                    "Predictive ML model indicates a fault pattern. "
                    "Sensor readings are near limits. Proactive inspection recommended."
                )
            })

        # ── Overall status ───────────────────────────────────────────────────
        if any(a["severity"] == "critical" for a in anomalies):
            overall_status = "critical"
        elif any(a["severity"] == "warning" for a in anomalies):
            overall_status = "warning"
        else:
            overall_status = "normal"

        return {
            "status": "success",
            "vehicle_id": vehicle_id,
            "overall_status": overall_status,
            "ml_label": ml_label,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "sensor_readings": {
                "engine_rpm": vd.get("engine_rpm"),
                "lub_oil_pressure": vd.get("lub_oil_pressure"),
                "fuel_pressure": vd.get("fuel_pressure"),
                "coolant_pressure": vd.get("coolant_pressure"),
                "lub_oil_temp": vd.get("lub_oil_temp"),
                "coolant_temp": vd.get("coolant_temp"),
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to run anomaly detection: {str(e)}"
        }


def get_all_vehicles_status() -> dict:
    """
    Retrieves a summary status of all vehicles in the fleet based on the
    6-sensor telemetry dataset. Useful for dashboard overview and triage.

    Returns:
        dict: List of all vehicles with current sensor readings and fault labels,
              sorted by severity (critical first).
    """
    try:
        with open(DATA_DIR / "telemetry_stream.json", "r") as f:
            telemetry_data = json.load(f)

        with open(DATA_DIR / "vehicles.json", "r") as f:
            vehicles = json.load(f)

        vehicle_statuses = []
        for vehicle in vehicles:
            vehicle_id = vehicle["vehicle_id"]
            td = telemetry_data.get(vehicle_id, {})

            ml_label = td.get("label", -1)
            vehicle_statuses.append({
                "vehicle_id": vehicle_id,
                "make": vehicle.get("make", "Unknown"),
                "model": vehicle.get("model", "Unknown"),
                "owner_name": vehicle.get("owner", {}).get("name", "Unknown"),
                "city": vehicle.get("owner", {}).get("city", "Unknown"),
                "ml_label": ml_label,
                "engine_rpm": td.get("engine_rpm"),
                "lub_oil_pressure": td.get("lub_oil_pressure"),
                "fuel_pressure": td.get("fuel_pressure"),
                "coolant_pressure": td.get("coolant_pressure"),
                "lub_oil_temp": td.get("lub_oil_temp"),
                "coolant_temp": td.get("coolant_temp"),
            })

        # Sort: fault (label=1) first, then normal (label=0)
        vehicle_statuses.sort(key=lambda x: (0 if x.get("ml_label") == 1 else 1))

        return {
            "status": "success",
            "total_vehicles": len(vehicle_statuses),
            "fault_count": sum(1 for v in vehicle_statuses if v.get("ml_label") == 1),
            "normal_count": sum(1 for v in vehicle_statuses if v.get("ml_label") == 0),
            "vehicles": vehicle_statuses
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve fleet status: {str(e)}"
        }
