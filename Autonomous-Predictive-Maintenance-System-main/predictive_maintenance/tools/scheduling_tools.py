"""Scheduling tools for managing appointments and service center operations."""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List

# Path to data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# In-memory storage for bookings (in production, this would be a database)
BOOKINGS = []


def get_available_slots(service_center_id: str, 
                        date_from: Optional[str] = None,
                        date_to: Optional[str] = None) -> dict:
    """
    Retrieves available appointment slots for a service center.
    
    Args:
        service_center_id: The unique identifier of the service center
        date_from: Optional start date for search (YYYY-MM-DD format)
        date_to: Optional end date for search (YYYY-MM-DD format)
        
    Returns:
        dict: List of available appointment slots with dates and times
    """
    try:
        with open(DATA_DIR / "service_centers.json", "r") as f:
            centers = json.load(f)
        
        center = next((c for c in centers if c["service_center_id"] == service_center_id), None)
        
        if not center:
            return {
                "status": "error",
                "error_message": f"Service center {service_center_id} not found"
            }
        
        available_slots = [
            slot for slot in center.get("available_slots", [])
            if slot.get("available", False)
        ]
        
        # Filter by date range if specified
        if date_from:
            available_slots = [s for s in available_slots if s["date"] >= date_from]
        if date_to:
            available_slots = [s for s in available_slots if s["date"] <= date_to]
        
        return {
            "status": "success",
            "service_center": {
                "id": center["service_center_id"],
                "name": center["name"],
                "city": center["city"],
                "address": center["address"],
                "phone": center["phone"]
            },
            "available_slots_count": len(available_slots),
            "slots": available_slots
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve available slots: {str(e)}"
        }


def get_nearest_service_center(city: str) -> dict:
    """
    Finds the nearest service center for a given city.
    
    Args:
        city: The city name to search for nearby service centers
        
    Returns:
        dict: Details of nearest service center(s) ordered by proximity
    """
    try:
        with open(DATA_DIR / "service_centers.json", "r") as f:
            centers = json.load(f)
        
        # Find centers in the same city first
        same_city = [c for c in centers if c["city"].lower() == city.lower()]
        
        if same_city:
            return {
                "status": "success",
                "city_searched": city,
                "centers_found": len(same_city),
                "service_centers": [
                    {
                        "service_center_id": c["service_center_id"],
                        "name": c["name"],
                        "address": c["address"],
                        "phone": c["phone"],
                        "capacity_per_day": c["capacity_per_day"],
                        "available_slots": len([s for s in c["available_slots"] if s["available"]])
                    }
                    for c in same_city
                ]
            }
        else:
            # Return all centers if none in the same city
            return {
                "status": "success",
                "city_searched": city,
                "message": f"No service centers found in {city}. Showing all available centers.",
                "centers_found": len(centers),
                "service_centers": [
                    {
                        "service_center_id": c["service_center_id"],
                        "name": c["name"],
                        "city": c["city"],
                        "address": c["address"],
                        "phone": c["phone"]
                    }
                    for c in centers
                ]
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to find service centers: {str(e)}"
        }


def book_appointment(vehicle_id: str,
                     slot_id: str,
                     service_type: str,
                     predicted_issues: List[str],
                     estimated_duration_hours: float = 2.0,
                     customer_notes: str = "") -> dict:
    """
    Books a service appointment for a vehicle.
    
    Args:
        vehicle_id: The unique identifier of the vehicle
        slot_id: The ID of the available slot to book
        service_type: Type of service ('maintenance', 'repair', 'emergency', 'diagnostic')
        predicted_issues: List of issues predicted by the diagnosis agent
        estimated_duration_hours: Estimated service duration in hours
        customer_notes: Any additional notes from the customer
        
    Returns:
        dict: Booking confirmation with appointment details
    """
    global BOOKINGS
    
    try:
        with open(DATA_DIR / "service_centers.json", "r") as f:
            centers = json.load(f)
        
        with open(DATA_DIR / "vehicles.json", "r") as f:
            vehicles = json.load(f)
        
        # Find the slot
        slot_found = None
        center_found = None
        for center in centers:
            for slot in center.get("available_slots", []):
                if slot["slot_id"] == slot_id:
                    slot_found = slot
                    center_found = center
                    break
            if slot_found:
                break
        
        if not slot_found:
            return {
                "status": "error",
                "error_message": f"Slot {slot_id} not found"
            }
        
        if not slot_found.get("available", False):
            return {
                "status": "error",
                "error_message": f"Slot {slot_id} is no longer available"
            }
        
        # Get vehicle and owner info
        vehicle = next((v for v in vehicles if v["vehicle_id"] == vehicle_id), None)
        if not vehicle:
            return {
                "status": "error",
                "error_message": f"Vehicle {vehicle_id} not found"
            }
        
        # Create booking
        booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        booking = {
            "booking_id": booking_id,
            "vehicle_id": vehicle_id,
            "vehicle": f"{vehicle['make']} {vehicle['model']}",
            "owner_name": vehicle["owner"]["name"],
            "owner_phone": vehicle["owner"]["phone"],
            "service_center_id": center_found["service_center_id"],
            "service_center_name": center_found["name"],
            "slot_id": slot_id,
            "date": slot_found["date"],
            "time": slot_found["time"],
            "service_type": service_type,
            "predicted_issues": predicted_issues,
            "estimated_duration_hours": estimated_duration_hours,
            "customer_notes": customer_notes,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        BOOKINGS.append(booking)
        
        # Mark slot as unavailable (in memory only for demo)
        slot_found["available"] = False
        
        return {
            "status": "success",
            "message": "Appointment booked successfully",
            "booking": booking,
            "confirmation_message": (
                f"Your appointment has been confirmed for {slot_found['date']} at "
                f"{slot_found['time']} at {center_found['name']}, {center_found['city']}. "
                f"Booking reference: {booking_id}"
            )
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to book appointment: {str(e)}"
        }


def cancel_appointment(booking_id: str, reason: str = "") -> dict:
    """
    Cancels an existing appointment.
    
    Args:
        booking_id: The unique identifier of the booking to cancel
        reason: Optional reason for cancellation
        
    Returns:
        dict: Confirmation of cancellation
    """
    global BOOKINGS
    
    try:
        booking = next((b for b in BOOKINGS if b["booking_id"] == booking_id), None)
        
        if not booking:
            return {
                "status": "error",
                "error_message": f"Booking {booking_id} not found"
            }
        
        booking["status"] = "cancelled"
        booking["cancellation_reason"] = reason
        booking["cancelled_at"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": "Appointment cancelled successfully",
            "booking_id": booking_id,
            "refund_eligible": True,
            "rescheduling_available": True
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to cancel appointment: {str(e)}"
        }


def check_parts_availability(part_ids: List[str], 
                             service_center_id: str) -> dict:
    """
    Checks if required parts are available at a service center.
    
    Args:
        part_ids: List of part identifiers to check
        service_center_id: The service center to check inventory
        
    Returns:
        dict: Availability status for each part and alternatives if unavailable
    """
    try:
        with open(DATA_DIR / "service_centers.json", "r") as f:
            centers = json.load(f)
        
        center = next((c for c in centers if c["service_center_id"] == service_center_id), None)
        
        if not center:
            return {
                "status": "error",
                "error_message": f"Service center {service_center_id} not found"
            }
        
        inventory = center.get("parts_inventory", {})
        
        availability = []
        all_available = True
        
        for part_id in part_ids:
            quantity = inventory.get(part_id, 0)
            available = quantity > 0
            
            if not available:
                all_available = False
            
            availability.append({
                "part_id": part_id,
                "available": available,
                "quantity_in_stock": quantity,
                "estimated_restock_days": 0 if available else 3
            })
        
        return {
            "status": "success",
            "service_center_id": service_center_id,
            "all_parts_available": all_available,
            "parts": availability
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to check parts availability: {str(e)}"
        }


def reserve_parts(part_ids: List[str], 
                  service_center_id: str,
                  booking_id: str) -> dict:
    """
    Reserves parts for an upcoming service appointment.
    
    Args:
        part_ids: List of part identifiers to reserve
        service_center_id: The service center where parts should be reserved
        booking_id: The booking reference for which parts are reserved
        
    Returns:
        dict: Reservation confirmation
    """
    try:
        # In a real system, this would update the inventory
        return {
            "status": "success",
            "message": "Parts reserved successfully",
            "booking_id": booking_id,
            "reserved_parts": part_ids,
            "service_center_id": service_center_id,
            "reservation_expires": (datetime.now() + timedelta(days=7)).isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to reserve parts: {str(e)}"
        }


def get_technicians(service_center_id: str, 
                    skill_required: Optional[str] = None) -> dict:
    """
    Retrieves available technicians at a service center.
    
    Args:
        service_center_id: The service center to query
        skill_required: Optional skill filter (e.g., 'engine', 'electrical', 'brakes')
        
    Returns:
        dict: List of available technicians with their skills and availability
    """
    # Simulated technician data
    TECHNICIANS = {
        "TECH001": {"name": "Rajiv Kumar", "skills": ["engine", "transmission", "general"], "rating": 4.8},
        "TECH002": {"name": "Suresh Patel", "skills": ["electrical", "battery", "diagnostics"], "rating": 4.6},
        "TECH003": {"name": "Anil Sharma", "skills": ["brakes", "suspension", "general"], "rating": 4.9},
        "TECH004": {"name": "Mohammad Ali", "skills": ["engine", "ac", "cooling"], "rating": 4.7},
        "TECH005": {"name": "Ravi Verma", "skills": ["ac", "electrical", "general"], "rating": 4.5},
        "TECH006": {"name": "Deepak Singh", "skills": ["engine", "transmission", "diagnostics"], "rating": 4.8},
        "TECH007": {"name": "Prakash Joshi", "skills": ["brakes", "tyres", "suspension"], "rating": 4.6}
    }
    
    try:
        with open(DATA_DIR / "service_centers.json", "r") as f:
            centers = json.load(f)
        
        center = next((c for c in centers if c["service_center_id"] == service_center_id), None)
        
        if not center:
            return {
                "status": "error",
                "error_message": f"Service center {service_center_id} not found"
            }
        
        technician_ids = center.get("technicians", [])
        available_technicians = []
        
        for tech_id in technician_ids:
            if tech_id in TECHNICIANS:
                tech = TECHNICIANS[tech_id]
                
                # Filter by skill if specified
                if skill_required:
                    if skill_required.lower() not in [s.lower() for s in tech["skills"]]:
                        continue
                
                available_technicians.append({
                    "technician_id": tech_id,
                    "name": tech["name"],
                    "skills": tech["skills"],
                    "rating": tech["rating"],
                    "available": True  # Simplified for demo
                })
        
        return {
            "status": "success",
            "service_center_id": service_center_id,
            "technicians_count": len(available_technicians),
            "technicians": available_technicians
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to get technicians: {str(e)}"
        }


def assign_technician(booking_id: str, 
                      technician_id: str) -> dict:
    """
    Assigns a technician to a service appointment.
    
    Args:
        booking_id: The booking to assign a technician to
        technician_id: The technician to assign
        
    Returns:
        dict: Assignment confirmation
    """
    global BOOKINGS
    
    try:
        booking = next((b for b in BOOKINGS if b["booking_id"] == booking_id), None)
        
        if not booking:
            return {
                "status": "error",
                "error_message": f"Booking {booking_id} not found"
            }
        
        booking["assigned_technician_id"] = technician_id
        booking["technician_assigned_at"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": "Technician assigned successfully",
            "booking_id": booking_id,
            "technician_id": technician_id
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to assign technician: {str(e)}"
        }
