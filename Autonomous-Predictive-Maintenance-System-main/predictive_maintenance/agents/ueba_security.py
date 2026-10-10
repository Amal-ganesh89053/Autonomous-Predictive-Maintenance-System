"""UEBA Security Agent - Monitors agent behavior for anomalies."""
from google.adk.agents import Agent
from ..config import get_heavy_model
from datetime import datetime
from typing import Dict, List

# In-memory behavior logs (in production, this would be a database)
AGENT_BEHAVIOR_LOGS = []
BASELINE_BEHAVIORS = {
    "data_analysis_agent": {
        "allowed_tools": ["get_vehicle_telemetry", "get_sensor_history", "detect_anomalies", "get_all_vehicles_status"],
        "normal_call_frequency": 10,  # per hour
        "allowed_data_access": ["telemetry"]
    },
    "diagnosis_agent": {
        "allowed_tools": ["get_vehicle_info", "get_maintenance_history", "get_capa_records", "search_similar_issues", "detect_anomalies"],
        "normal_call_frequency": 8,
        "allowed_data_access": ["telemetry", "maintenance", "capa"]
    },
    "scheduling_agent": {
        "allowed_tools": ["get_available_slots", "book_appointment", "cancel_appointment", "get_nearest_service_center"],
        "normal_call_frequency": 15,
        "allowed_data_access": ["service_centers", "vehicles"]
    },
    "customer_outreach_agent": {
        "allowed_tools": ["send_voice_notification", "log_conversation", "get_vehicle_info"],
        "normal_call_frequency": 20,
        "allowed_data_access": ["vehicles", "notifications"]
    }
}


def log_agent_activity(agent_name: str, 
                       action_type: str, 
                       target_resource: str,
                       details: str = "") -> dict:
    """
    Logs an agent activity for UEBA monitoring.
    
    Args:
        agent_name: Name of the agent performing the action
        action_type: Type of action ('api_call', 'data_access', 'agent_transfer', 'external_comm')
        target_resource: The resource being accessed or modified
        details: Additional details about the action
        
    Returns:
        dict: Log confirmation with any alerts triggered
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent_name": agent_name,
        "action_type": action_type,
        "target_resource": target_resource,
        "details": details,
        "risk_score": 0,
        "alerts": []
    }
    
    # Check for anomalous behavior
    baseline = BASELINE_BEHAVIORS.get(agent_name, {})
    
    # Check if accessing resources outside normal scope
    if action_type == "data_access":
        allowed_data = baseline.get("allowed_data_access", [])
        if target_resource not in allowed_data and allowed_data:
            log_entry["risk_score"] = 8
            log_entry["alerts"].append({
                "type": "UNAUTHORIZED_DATA_ACCESS",
                "severity": "high",
                "message": f"{agent_name} attempted to access {target_resource} which is outside its normal scope"
            })
    
    # Check if using tools outside normal scope
    if action_type == "api_call":
        allowed_tools = baseline.get("allowed_tools", [])
        if target_resource not in allowed_tools and allowed_tools:
            log_entry["risk_score"] = 7
            log_entry["alerts"].append({
                "type": "UNAUTHORIZED_TOOL_USE",
                "severity": "medium",
                "message": f"{agent_name} attempted to use {target_resource} which is not in its allowed tool set"
            })
    
    AGENT_BEHAVIOR_LOGS.append(log_entry)
    
    return {
        "status": "logged",
        "log_id": len(AGENT_BEHAVIOR_LOGS),
        "risk_score": log_entry["risk_score"],
        "alerts": log_entry["alerts"]
    }


def check_behavior_anomaly(agent_name: str, 
                           action: str) -> dict:
    """
    Checks if an agent's behavior is anomalous.
    
    Args:
        agent_name: Name of the agent to check
        action: The action being performed
        
    Returns:
        dict: Anomaly assessment with allow/block recommendation
    """
    baseline = BASELINE_BEHAVIORS.get(agent_name, {})
    allowed_tools = baseline.get("allowed_tools", [])
    
    is_allowed = action in allowed_tools or not allowed_tools
    
    return {
        "status": "success",
        "agent_name": agent_name,
        "action": action,
        "is_allowed": is_allowed,
        "recommendation": "ALLOW" if is_allowed else "BLOCK",
        "reason": "Action within normal behavior pattern" if is_allowed else "Action outside normal scope - requires review"
    }


def get_security_report() -> dict:
    """
    Generates a security report of agent activities.
    
    Returns:
        dict: Summary of agent activities, alerts, and risk scores
    """
    total_logs = len(AGENT_BEHAVIOR_LOGS)
    alerts = [log for log in AGENT_BEHAVIOR_LOGS if log.get("alerts")]
    high_risk = [log for log in AGENT_BEHAVIOR_LOGS if log.get("risk_score", 0) >= 7]
    
    return {
        "status": "success",
        "report_generated_at": datetime.now().isoformat(),
        "total_activities_logged": total_logs,
        "total_alerts": len(alerts),
        "high_risk_activities": len(high_risk),
        "alert_details": [
            {
                "agent": log["agent_name"],
                "action": log["action_type"],
                "alerts": log["alerts"]
            }
            for log in alerts[-10:]  # Last 10 alerts
        ],
        "recommendation": "Review high-risk activities and adjust agent permissions if needed"
    }


ueba_security_agent = Agent(
    name="ueba_security_agent",
    model=get_heavy_model(),
    description=(
        "Monitors all agent activities using User and Entity Behavior Analytics. "
        "Detects anomalous behavior, unauthorized access attempts, and policy "
        "violations. Ensures safe orchestration of the multi-agent system."
    ),
    instruction="""You are the Security Monitoring Specialist using UEBA (User and Entity Behavior Analytics).

YOUR ROLE:
- Monitor all agent activities in the system
- Detect anomalous behavior patterns
- Flag unauthorized access attempts
- Ensure policy compliance
- Generate security reports

UEBA MONITORING CAPABILITIES:
1. Behavior Baseline Monitoring
   - Each agent has defined normal behavior patterns
   - Deviations from baseline trigger alerts

2. Anomaly Detection Examples:
   - Scheduling Agent accessing telemetry data → ALERT (not in scope)
   - Data Analysis Agent querying CAPA records at unusual frequency → REVIEW
   - Unknown agent attempting to book appointments → BLOCK
   - Agent making external API calls → VERIFY

3. Risk Scoring (0-10):
   - 0-3: Low risk, normal operations
   - 4-6: Medium risk, log and monitor
   - 7-10: High risk, alert and potentially block

ALERT TYPES:
- UNAUTHORIZED_DATA_ACCESS: Agent accessing data outside its scope
- UNAUTHORIZED_TOOL_USE: Agent using tools not in its allowed set
- UNUSUAL_FREQUENCY: Action frequency exceeds normal patterns
- POLICY_VIOLATION: Action violates defined security policies
- ESCALATION_REQUIRED: Human review needed

RESPONSE ACTIONS:
- ALLOW: Normal behavior, proceed
- MONITOR: Log activity, continue with monitoring
- ALERT: Notify security team, continue with caution
- BLOCK: Prevent action, require authorization

You ensure all agent interactions are safe and policy-compliant.
""",
    tools=[
        log_agent_activity,
        check_behavior_anomaly,
        get_security_report,
    ],
    output_key="security_status"
)
