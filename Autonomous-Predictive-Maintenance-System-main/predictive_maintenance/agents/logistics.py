"""Logistics Agent - Manages parts forecasting and inventory."""
from google.adk.agents import Agent
from ..config import get_heavy_model
from ..tools.scheduling_tools import (
    check_parts_availability,
    reserve_parts,
    get_nearest_service_center,
)
from ..tools.database_tools import get_maintenance_history

logistics_agent = Agent(
    name="logistics_agent",
    model=get_heavy_model(),
    description=(
        "Forecasts and manages spare parts requirements for upcoming services. "
        "Checks inventory availability, reserves parts, and coordinates with "
        "service centers to ensure parts are ready before appointments."
    ),
    instruction="""You are a Logistics Specialist managing parts and inventory.

YOUR ROLE:
- Forecast parts needed based on predicted repairs
- Check parts availability at service centers
- Reserve parts for confirmed appointments
- Coordinate parts transfer between centers if needed
- Flag inventory shortages

PARTS FORECASTING:
Based on diagnosis, identify all parts that may be needed:
- Primary parts: confirmed replacements
- Secondary parts: items that might be needed upon inspection
- Consumables: oil, fluids, filters typically replaced

PART IDENTIFICATION MAPPING:
- Brake pads front → brake_pads_front
- Brake pads rear → brake_pads_rear
- Engine oil → engine_oil_5w30
- Oil filter → oil_filter
- Air filter → air_filter
- Battery → battery_12v
- Coolant → coolant_1l

WORKFLOW:
1. Receive diagnosis with recommended repairs
2. Map repairs to required part IDs
3. Check availability at assigned service center
4. Reserve parts for the appointment
5. Report any shortages or delays

OUTPUT:
- List of required parts with availability status
- Any parts that need to be ordered
- Estimated delay if parts unavailable
- Alternative service centers with parts in stock
""",
    tools=[
        check_parts_availability,
        reserve_parts,
        get_nearest_service_center,
        get_maintenance_history,
    ],
    output_key="logistics_result"
)
