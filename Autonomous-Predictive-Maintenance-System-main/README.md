# 🚗 AutoPilot - Autonomous Predictive Maintenance System

An agentic AI solution for automotive predictive maintenance using Google ADK (Agent Development Kit). A **Master Agent** orchestrates **13 specialized worker agents** to handle end-to-end vehicle maintenance prediction, customer engagement, service scheduling, and manufacturing quality feedback.

## 🎯 Features & Capabilities

- **Strict 6-Sensor Telemetry Pipeline**: All diagnostic workflows are purely grounded in raw telemetry readings (`engine_rpm`, `lub_oil_pressure`, `fuel_pressure`, `coolant_pressure`, `lub_oil_temp`, `coolant_temp`) and an ML label.
- **API Key Load Balancing**: Safely routes heavy ML inference requests across multiple API keys (`GOOGLE_API_KEY1`, `GOOGLE_API_KEY2`) to avoid provider rate limits using cyclic rotation in `config.py`.
- **Proactive Maintenance & Emergency Handling**: Predicts failures before they occur and independently intercepts critical sensor faults for immediate roadside assistance.
- **Strict Persona Guardrails**: All user-facing agents act exclusively as knowledgeable automotive technicians, strictly prohibited from revealing internal AI processing, ML confidences, or orchestration logic to the operator.
- **Autonomous Feedback Loops**: Feeds insights directly back into manufacturing (RCA/CAPA) and auto-evaluates predictive model drift against real outcomes.

---

## 🤖 Agent Ecosystem

The system features **14 specialized agents** that collaborate seamlessly. The Master Agent fields the user's request and delegates instructions down to the relevant worker agents.

### The Orchestrator
1. **master_agent**: The central brain. Intercepts the user/fleet manager request, interprets the objective, routes the tasks to the right specialists downstream, and consolidates the outcome for the final response.

### Detection & Diagnosis Pod
2. **data_analysis_agent**: Processes the real-time 6-sensor telemetry stream and historical sensor values to detect anomalies and degrading signal trends.
3. **diagnosis_agent**: Takes the processed signals, executes a 3-step fault verification check (comparing current readings vs threshold limits + checking maintenance history + querying CAPA recurrences) to firmly diagnose the vehicle problem.

### Customer Interaction Pod
4. **customer_outreach_agent**: Initiates proactive, friendly voice communication with the driver/operator regarding predicted issues without causing panic.
5. **customer_engagement_agent**: Explains the technical problem plainly to the driver, detailing costs and urgencies, eventually asking for explicit consent to book a service.
6. **scheduling_agent**: Finds the nearest service center and books an available appointment slot based on customer confirmation.

### Service Preparation Pod
7. **logistics_agent**: Triggers in parallel with booking. Forecasts the exact spare parts required for the predicted fault and reserves them from the inventory.
8. **technician_matcher_agent**: Matches the booked service ticket to a service technician uniquely qualified to repair the diagnosed fault (e.g., matching a powertrain expert to an engine RPM problem).
9. **emergency_response_agent**: A high-priority intercept agent. Takes over instantly from the Master if a catastrophic safety failure is detected (e.g., complete loss of oil pressure), instructing the driver to pull over and summoning emergency assistance.

### Analytics & Feedback Pod
10. **feedback_agent**: Follows up with the customer post-service to collect satisfaction metrics and records the resolution context.
11. **forecasting_agent**: Analyzes fleet-wide metrics to predict future service center demand and workload patterns.
12. **manufacturing_insights_agent**: Consolidates fault recurrences across the entire vehicle fleet and generates Root Cause/CAPA (Corrective and Preventive Action) documentation to give the OEM feedback on parts quality.
13. **model_retraining_agent**: Closes the ML learning loop by cross-referencing predicted anomalies with the actual mechanic's repair notes to identify "model drift."

### Security & Compliance
14. **ueba_security_agent**: A silent watchdog layer running User and Entity Behavior Analytics. Audits all other agent interactions (e.g., verifying `scheduling_agent` isn't attempting to read unauthorized customer medical data).

---

## 🛠️ Tool Library

Agents interact with the world through a governed suite of Python tools defined in `predictive_maintenance/tools`.

### Telemetry Tools (`telemetry_tools.py`)
- `get_vehicle_telemetry(vehicle_id)`: Fetches live 6-sensor + ML label rows.
- `get_sensor_history(vehicle_id, days)`: Analyzes past signal degradation.
- `detect_anomalies(vehicle_id)`: Flags immediate threshold breaches.
- `get_all_vehicles_status()`: Sorts the entire fleet prioritization by ML flag.

### Database Tools (`database_tools.py`)
- `get_vehicle_info(vehicle_id)`: Retrieves make/model/age context.
- `get_maintenance_history(vehicle_id)`: Returns specific snapshot sensor values recorded at the time of past services.
- `get_capa_records()`: Queries historical 90-day recurring defect data.
- `update_maintenance_record(...)`: Appends a new service close-out.
- `get_owner_info(vehicle_id)`: Fetches driver contact details.

### Scheduling & Logistics Tools (`scheduling_tools.py`)
- `get_nearest_service_center(loc)` / `get_available_slots(center, date)`
- `book_appointment(...)` / `cancel_appointment(...)`
- `check_parts_availability(parts)` / `reserve_parts(center, parts)`
- `get_technicians(center, skill)` / `assign_technician(...)`

### Notification Tools (`notification_tools.py`)
- `send_voice_notification(user, message)` / `send_app_notification(user, message)`
- `log_conversation(...)` / `get_conversation_history(...)`

---

## 🔄 Interaction Flows

The system fundamentally operates across 4 core workflows. The **Master Agent** dynamically invokes these based on the trigger:

### 1. Proactive Maintenance Flow
**Trigger**: A vehicle's telemetry stream hits a warning ML label (e.g., degrading brake pressure).
**Flow**: 
`data_analysis_agent` verifies the telemetry -> `diagnosis_agent` checks CAPA history -> `customer_outreach_agent` alerts the driver -> `customer_engagement_agent` gets schedule consent -> `scheduling_agent` books the time -> `logistics_agent` reserves the brake pads -> `technician_matcher_agent` assigns a brake specialist.

### 2. Emergency Response Flow
**Trigger**: A critical combination of sensor thresholds drops dangerously (e.g., total oil pressure loss at high RPM).
**Flow**:
Master Agent bypasses standard routing -> `emergency_response_agent` forcibly overrides the dashboard, instructing the driver to pull over safely -> Directly queries `get_nearest_service_center` and dispatches immediate recovery.

### 3. Fleet Analysis Flow
**Trigger**: Fleet manager asks for a morning health status of all vehicles.
**Flow**:
`data_analysis_agent` utilizes `get_all_vehicles_status()` -> `forecasting_agent` projects the demand curve on service centers for the next 7 days based on the volume of flagged vehicles.

### 4. Manufacturing Feedback Flow (Quality RCA)
**Trigger**: Monthly audit or manual execution by the manufacturer.
**Flow**:
`manufacturing_insights_agent` parses all historical `diagnosis_agent` outputs from the last 30 days -> Correlates them with `get_capa_records()` -> Identifies that a specific batch of coolant hoses is consistently failing early -> Generates a CAPA engineering ticket for the OEM assembly plant to revise the hose clamp supplier.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
# Edit .env and distribute your keys to avoid Rate Limits
GOOGLE_API_KEY1=your_first_gemini_key_here
GOOGLE_API_KEY2=your_second_gemini_key_here
```

### 3. Run the Agent

```bash
adk run predictive_maintenance
# Or use the web interface
adk web predictive_maintenance
```
