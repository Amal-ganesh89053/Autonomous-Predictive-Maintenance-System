"""Tools for Predictive Maintenance Agents."""
from .telemetry_tools import (
    get_vehicle_telemetry,
    get_sensor_history,
    detect_anomalies,
    get_all_vehicles_status,
)
from .database_tools import (
    get_vehicle_info,
    get_maintenance_history,
    get_capa_records,
    update_maintenance_record,
    get_owner_info,
)
from .scheduling_tools import (
    get_available_slots,
    book_appointment,
    cancel_appointment,
    get_nearest_service_center,
    check_parts_availability,
    reserve_parts,
    get_technicians,
    assign_technician,
)
from .notification_tools import (
    send_voice_notification,
    send_app_notification,
    log_conversation,
    get_conversation_history,
)

__all__ = [
    # Telemetry
    "get_vehicle_telemetry",
    "get_sensor_history", 
    "detect_anomalies",
    "get_all_vehicles_status",
    # Database
    "get_vehicle_info",
    "get_maintenance_history",
    "get_capa_records",
    "update_maintenance_record",
    "get_owner_info",
    # Scheduling
    "get_available_slots",
    "book_appointment",
    "cancel_appointment",
    "get_nearest_service_center",
    "check_parts_availability",
    "reserve_parts",
    "get_technicians",
    "assign_technician",
    # Notifications
    "send_voice_notification",
    "send_app_notification",
    "log_conversation",
    "get_conversation_history",
]
