"""Notification tools for customer communication."""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Path to data directory  
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# In-memory storage for conversations and notifications
CONVERSATIONS = []
NOTIFICATIONS = []


def send_voice_notification(vehicle_id: str, 
                            message: str,
                            priority: str = "normal") -> dict:
    """
    Sends a voice notification to the vehicle owner through the in-car 
    voice interface. This simulates the primary communication channel.
    
    Args:
        vehicle_id: The unique identifier of the vehicle
        message: The message to be spoken to the driver
        priority: Message priority ('low', 'normal', 'high', 'critical')
        
    Returns:
        dict: Confirmation of notification delivery
    """
    try:
        with open(DATA_DIR / "vehicles.json", "r") as f:
            vehicles = json.load(f)
        
        vehicle = next((v for v in vehicles if v["vehicle_id"] == vehicle_id), None)
        
        if not vehicle:
            return {
                "status": "error",
                "error_message": f"Vehicle {vehicle_id} not found"
            }
        
        notification = {
            "notification_id": f"VN{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "voice",
            "vehicle_id": vehicle_id,
            "owner_id": vehicle["owner"]["owner_id"],
            "owner_name": vehicle["owner"]["name"],
            "message": message,
            "priority": priority,
            "channel": "in_car_voice",
            "timestamp": datetime.now().isoformat(),
            "status": "delivered"
        }
        
        NOTIFICATIONS.append(notification)
        
        # Simulate voice response
        response_text = f"""
🔊 IN-CAR VOICE ASSISTANT - {vehicle['make']} {vehicle['model']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Speaking to {vehicle['owner']['name']}]

"{message}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: DELIVERED | Priority: {priority.upper()}
"""
        
        return {
            "status": "success",
            "message": "Voice notification sent successfully",
            "notification": notification,
            "voice_output": response_text
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to send voice notification: {str(e)}"
        }


def send_app_notification(owner_id: str,
                          title: str,
                          message: str,
                          action_type: Optional[str] = None,
                          action_data: Optional[dict] = None) -> dict:
    """
    Sends a push notification to the owner's mobile app.
    This is the secondary communication channel.
    
    Args:
        owner_id: The unique identifier of the owner
        title: Notification title
        message: Notification body message
        action_type: Optional action type ('book_service', 'view_details', 'call_support')
        action_data: Optional data for the action (e.g., deep link parameters)
        
    Returns:
        dict: Confirmation of notification delivery
    """
    try:
        with open(DATA_DIR / "vehicles.json", "r") as f:
            vehicles = json.load(f)
        
        owner = None
        for vehicle in vehicles:
            if vehicle["owner"]["owner_id"] == owner_id:
                owner = vehicle["owner"]
                break
        
        if not owner:
            return {
                "status": "error",
                "error_message": f"Owner {owner_id} not found"
            }
        
        notification = {
            "notification_id": f"AN{datetime.now().strftime('%Y%m%d%H%M%S')}", 
            "type": "app_push",
            "owner_id": owner_id,
            "owner_name": owner["name"],
            "title": title,
            "message": message,
            "action_type": action_type,
            "action_data": action_data,
            "timestamp": datetime.now().isoformat(),
            "status": "delivered"
        }
        
        NOTIFICATIONS.append(notification)
        
        return {
            "status": "success",
            "message": "App notification sent successfully",
            "notification": notification,
            "app_preview": f"""
📱 MOBILE APP NOTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
To: {owner['name']}

🔔 {title}

{message}

{f'[{action_type.replace("_", " ").title()}]' if action_type else ''}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to send app notification: {str(e)}"
        }


def log_conversation(vehicle_id: str,
                     agent_name: str,
                     conversation_type: str,
                     messages: List[dict],
                     outcome: str,
                     customer_consent: Optional[bool] = None) -> dict:
    """
    Logs a conversation between an agent and a customer.
    Required for compliance and analytics.
    
    Args:
        vehicle_id: The vehicle the conversation is about
        agent_name: Name of the agent handling the conversation
        conversation_type: Type of conversation ('outreach', 'engagement', 
                          'scheduling', 'feedback', 'emergency')
        messages: List of message objects with 'role' and 'content'
        outcome: Outcome of conversation ('service_booked', 'declined', 
                'rescheduled', 'escalated', 'feedback_collected')
        customer_consent: Whether customer gave consent for service
        
    Returns:
        dict: Conversation log confirmation
    """
    try:
        conversation = {
            "conversation_id": f"CV{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "vehicle_id": vehicle_id,
            "agent_name": agent_name,
            "conversation_type": conversation_type,
            "messages": messages,
            "outcome": outcome,
            "customer_consent": customer_consent,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": len(messages) * 15  # Estimate
        }
        
        CONVERSATIONS.append(conversation)
        
        return {
            "status": "success",
            "message": "Conversation logged successfully",
            "conversation_id": conversation["conversation_id"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to log conversation: {str(e)}"
        }


def get_conversation_history(vehicle_id: str,
                             conversation_type: Optional[str] = None,
                             limit: int = 10) -> dict:
    """
    Retrieves conversation history for a vehicle.
    
    Args:
        vehicle_id: The vehicle to get conversations for
        conversation_type: Optional filter by conversation type
        limit: Maximum number of conversations to return
        
    Returns:
        dict: List of past conversations
    """
    try:
        filtered = [c for c in CONVERSATIONS if c["vehicle_id"] == vehicle_id]
        
        if conversation_type:
            filtered = [c for c in filtered if c["conversation_type"] == conversation_type]
        
        # Sort by timestamp (most recent first)
        filtered.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "status": "success",
            "vehicle_id": vehicle_id,
            "total_conversations": len(filtered),
            "conversations": filtered[:limit]
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve conversation history: {str(e)}"
        }


def simulate_customer_response(prompt_type: str, 
                               vehicle_id: str) -> dict:
    """
    Simulates a customer response for demo purposes.
    In production, this would be replaced by actual voice/text input.
    
    Args:
        prompt_type: Type of prompt ('consent', 'scheduling', 'feedback', 'emergency')
        vehicle_id: The vehicle ID for context
        
    Returns:
        dict: Simulated customer response
    """
    # Simulated responses based on prompt type
    RESPONSES = {
        "consent": {
            "VH001": {"response": "yes", "text": "Yes, please book a service for me."},
            "VH002": {"response": "yes", "text": "Okay, I'll get it checked. What time slots are available?"},
            "VH003": {"response": "no", "text": "Not right now, I'll think about it."},
            "VH004": {"response": "yes", "text": "That sounds concerning. Yes, please schedule it soon."},
            "VH005": {"response": "later", "text": "Can we schedule it for next week instead?"},
            "VH006": {"response": "yes", "text": "This is urgent, please book the earliest available slot!"},
            "default": {"response": "yes", "text": "Yes, please proceed with the booking."}
        },
        "scheduling": {
            "VH001": {"response": "morning", "text": "Morning slot works best for me."},
            "VH002": {"response": "afternoon", "text": "I prefer afternoon, after 2 PM."},
            "default": {"response": "flexible", "text": "I'm flexible, any slot works."}
        },
        "feedback": {
            "VH001": {"response": "positive", "rating": 5, "text": "Excellent service! Very happy with the work."},
            "VH002": {"response": "positive", "rating": 4, "text": "Good service, but waiting time was a bit long."},
            "default": {"response": "positive", "rating": 4, "text": "Satisfied with the service."}
        },
        "emergency": {
            "VH006": {"response": "accept", "text": "Yes, I need immediate assistance! Where should I go?"},
            "default": {"response": "accept", "text": "I understand the urgency. Please help me."}
        }
    }
    
    responses = RESPONSES.get(prompt_type, RESPONSES["consent"])
    response = responses.get(vehicle_id, responses["default"])
    
    return {
        "status": "success",
        "prompt_type": prompt_type,
        "vehicle_id": vehicle_id,
        "customer_response": response
    }
