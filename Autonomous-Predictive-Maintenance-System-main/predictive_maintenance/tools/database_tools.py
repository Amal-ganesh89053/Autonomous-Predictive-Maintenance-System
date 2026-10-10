"""Database tools for accessing vehicle, maintenance, and CAPA records."""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Path to data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def get_vehicle_info(vehicle_id: str) -> dict:
    """
    Retrieves complete vehicle information including owner details.
    
    Args:
        vehicle_id: The unique identifier of the vehicle (e.g., 'VH001')
        
    Returns:
        dict: Vehicle details including make, model, year, VIN, registration,
              mileage, and owner contact information.
    """
    try:
        with open(DATA_DIR / "vehicles.json", "r") as f:
            vehicles = json.load(f)
        
        for vehicle in vehicles:
            if vehicle["vehicle_id"] == vehicle_id:
                return {
                    "status": "success",
                    "data": vehicle
                }
        
        return {
            "status": "error",
            "error_message": f"Vehicle {vehicle_id} not found"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve vehicle info: {str(e)}"
        }


def get_owner_info(owner_id: str) -> dict:
    """
    Retrieves owner information by owner ID.
    
    Args:
        owner_id: The unique identifier of the owner (e.g., 'OW001')
        
    Returns:
        dict: Owner details including name, phone, email, city, and 
              preferred contact method.
    """
    try:
        with open(DATA_DIR / "vehicles.json", "r") as f:
            vehicles = json.load(f)
        
        for vehicle in vehicles:
            if vehicle["owner"]["owner_id"] == owner_id:
                return {
                    "status": "success",
                    "data": {
                        "owner": vehicle["owner"],
                        "vehicle_id": vehicle["vehicle_id"],
                        "vehicle": f"{vehicle['make']} {vehicle['model']} ({vehicle['year']})"
                    }
                }
        
        return {
            "status": "error",
            "error_message": f"Owner {owner_id} not found"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve owner info: {str(e)}"
        }


def get_maintenance_history(vehicle_id: str, limit: Optional[int] = None) -> dict:
    """
    Retrieves the maintenance history for a specific vehicle.
    
    Args:
        vehicle_id: The unique identifier of the vehicle
        limit: Optional maximum number of records to return (most recent first)
        
    Returns:
        dict: List of maintenance records with service details, costs, and 
              any issues found during previous services.
    """
    try:
        with open(DATA_DIR / "maintenance_history.json", "r") as f:
            all_records = json.load(f)
        
        # Filter records for this vehicle
        vehicle_records = [r for r in all_records if r["vehicle_id"] == vehicle_id]
        
        # Sort by date (most recent first)
        vehicle_records.sort(key=lambda x: x["date"], reverse=True)
        
        # Apply limit if specified
        if limit:
            vehicle_records = vehicle_records[:limit]
        
        # Calculate some statistics
        total_cost = sum(r.get("cost_inr", 0) for r in vehicle_records)
        issues_found = []
        for r in vehicle_records:
            issues_found.extend(r.get("issues_found", []))
        
        return {
            "status": "success",
            "vehicle_id": vehicle_id,
            "total_records": len(vehicle_records),
            "total_spent_inr": total_cost,
            "recurring_issues": list(set(issues_found)),
            "records": vehicle_records
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve maintenance history: {str(e)}"
        }


def get_capa_records(component_type: Optional[str] = None, 
                     model: Optional[str] = None) -> dict:
    """
    Retrieves Corrective and Preventive Action (CAPA) records.
    Used for root cause analysis and identifying known defects.
    
    Args:
        component_type: Optional filter by component (e.g., 'battery', 'brake_pads')
        model: Optional filter by vehicle model (e.g., 'XUV700', 'Creta')
        
    Returns:
        dict: List of CAPA records with root cause analysis, affected models,
              corrective actions, and manufacturing feedback.
    """
    try:
        with open(DATA_DIR / "capa_records.json", "r") as f:
            all_records = json.load(f)
        
        filtered_records = all_records
        
        # Filter by component type if specified
        if component_type:
            filtered_records = [
                r for r in filtered_records 
                if component_type.lower() in r["component"].lower()
            ]
        
        # Filter by model if specified
        if model:
            filtered_records = [
                r for r in filtered_records 
                if model in r.get("affected_models", [])
            ]
        
        # Group by severity for summary
        severity_counts = {}
        for record in filtered_records:
            severity = record.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "status": "success",
            "total_records": len(filtered_records),
            "severity_summary": severity_counts,
            "records": filtered_records
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve CAPA records: {str(e)}"
        }


def update_maintenance_record(vehicle_id: str, 
                              service_type: str,
                              components_serviced: list,
                              issues_found: list,
                              cost_inr: float,
                              technician_id: str,
                              service_center_id: str,
                              notes: str) -> dict:
    """
    Adds a new maintenance record for a vehicle.
    Called after service completion to update the vehicle's history.
    
    Args:
        vehicle_id: The unique identifier of the vehicle
        service_type: Type of service ('scheduled_maintenance', 'repair', 'emergency')
        components_serviced: List of components that were serviced
        issues_found: List of any issues discovered during service
        cost_inr: Total cost of service in INR
        technician_id: ID of the technician who performed the service
        service_center_id: ID of the service center
        notes: Additional notes about the service
        
    Returns:
        dict: Confirmation of the new record or error message
    """
    try:
        with open(DATA_DIR / "maintenance_history.json", "r") as f:
            all_records = json.load(f)
        
        # Get current mileage from telemetry
        with open(DATA_DIR / "vehicles.json", "r") as f:
            vehicles = json.load(f)
        
        vehicle = next((v for v in vehicles if v["vehicle_id"] == vehicle_id), None)
        if not vehicle:
            return {
                "status": "error",
                "error_message": f"Vehicle {vehicle_id} not found"
            }
        
        # Generate new record ID
        new_id = f"MR{str(len(all_records) + 1).zfill(3)}"
        
        new_record = {
            "record_id": new_id,
            "vehicle_id": vehicle_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "service_type": service_type,
            "mileage_at_service": vehicle["mileage_km"],
            "components_serviced": components_serviced,
            "issues_found": issues_found,
            "dtc_codes": [],
            "technician_id": technician_id,
            "service_center_id": service_center_id,
            "cost_inr": cost_inr,
            "notes": notes
        }
        
        all_records.append(new_record)
        
        # In a real system, we would write this back to the database
        # For demo purposes, we just return success
        return {
            "status": "success",
            "message": "Maintenance record created successfully",
            "record_id": new_id,
            "record": new_record
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create maintenance record: {str(e)}"
        }


def search_similar_issues(component: str, issue_type: str) -> dict:
    """
    Searches for similar issues across the fleet and CAPA database.
    Useful for identifying patterns and known solutions.
    
    Args:
        component: Component type (e.g., 'battery', 'brakes', 'engine')
        issue_type: Type of issue (e.g., 'degradation', 'wear', 'failure')
        
    Returns:
        dict: Similar issues from fleet history and CAPA records with 
              recommended solutions.
    """
    try:
        # Search maintenance history
        with open(DATA_DIR / "maintenance_history.json", "r") as f:
            maintenance = json.load(f)
        
        with open(DATA_DIR / "capa_records.json", "r") as f:
            capa = json.load(f)
        
        # Find similar maintenance records
        similar_maintenance = []
        for record in maintenance:
            for issue in record.get("issues_found", []):
                if component.lower() in issue.lower() or issue_type.lower() in issue.lower():
                    similar_maintenance.append({
                        "record_id": record["record_id"],
                        "vehicle_id": record["vehicle_id"],
                        "date": record["date"],
                        "issue": issue,
                        "resolution": record.get("notes", "")
                    })
        
        # Find relevant CAPA records
        relevant_capa = []
        for record in capa:
            if (component.lower() in record["component"].lower() or 
                issue_type.lower() in record.get("defect_type", "").lower()):
                relevant_capa.append({
                    "capa_id": record["capa_id"],
                    "component": record["component"],
                    "root_cause": record["root_cause"],
                    "corrective_action": record["corrective_action"],
                    "affected_models": record["affected_models"]
                })
        
        return {
            "status": "success",
            "similar_issues_count": len(similar_maintenance),
            "capa_records_count": len(relevant_capa),
            "similar_maintenance_issues": similar_maintenance[:10],  # Limit to 10
            "relevant_capa_records": relevant_capa
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to search similar issues: {str(e)}"
        }
