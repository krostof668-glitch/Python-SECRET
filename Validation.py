import datetime
import json
import logging
import sys
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator

# 1. CONFIGURE SERVER LOGGING 
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("server_validation")

# -------------------------------------------------------------
# 2. INBOUND DATA MODELS (Input Validation Gate)
# -------------------------------------------------------------
class DeviceConfigSchema(BaseModel):
    device_name: str = Field(..., min_length=2, max_length=50)
    ip_address: str
    status: str = Field(default="active")

    @field_validator('status')
    @classmethod
    def validate_status(cls, value: str) -> str:
        """Custom validator enforcing explicit state choices."""
        allowed = {"active", "maintenance", "offline"}
        if value.lower() not in allowed:
            raise ValueError(f"Status must be one of: {allowed}")
        return value.lower()


class ServerRegistrationInput(BaseModel):
    """Firewall for incoming user payload schemas arriving at endpoints."""
    username: str = Field(..., min_length=4, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr # Enforces standard syntactic validation (e.g., must contain @ and a domain)
    age: int = Field(..., ge=18, le=120) # Enforces age limits between 18 and 120
    devices: List[DeviceConfigSchema] = Field(default=[]) # Nested data structure parsing


# -------------------------------------------------------------
# 3. OUTBOUND DATA MODELS (Safe Data Serialization)
# -------------------------------------------------------------
class SafeUserResponse(BaseModel):
    """Filters out secret data structures before delivering payloads to clients."""
    user_id: int
    username: str
    email: EmailStr
    is_active: bool = True
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    class Config:
        # Prevents client code from crashing if the system appends unknown telemetry fields later
        extra = "ignore" 


# -------------------------------------------------------------
# 4. SIMULATING SERVER DATA PROCESSING
# -------------------------------------------------------------
def process_inbound_api_request(json_payload_string: str) -> Optional[ServerRegistrationInput]:
    """Parses, type-checks, and cleans raw inbound client strings."""
    try:
        # Load raw data payload dictionary mapping 
        raw_data = json.loads(json_payload_string)
        
        # Trigger validation layer validation
        validated_data = ServerRegistrationInput(**raw_data)
        logger.info(f"API Gate: Data validated successfully for user '{validated_data.username}'.")
        return validated_data
        
    except ValidationError as e:
        # Captures granular structure metrics detailing exact syntax breaks back to the calling client
        logger.error(f"API Gate rejected malicious/malformed request:\n{e.json(indent=2)}")
        return None
    except json.JSONDecodeError:
        logger.error("API Gate rejected payload: Invalid JSON string serialization structure.")
        return None


# -------------------------------------------------------------
# RUNNING THE DATA PILLARS
# -------------------------------------------------------------
if __name__ == "__main__":
    print("--- 1. Processing Malformed Server Input ---")
    bad_client_json = """
    {
        "username": "bad$user", 
        "email": "not-valid-email",
        "age": 12,
        "devices": [
            {"device_name": "S", "ip_address": "192.168.1.1", "status": "exploit_state"}
        ]
    }
    """
    process_inbound_api_request(bad_client_json)


    print("\n--- 2. Processing Valid Server Input ---")
    good_client_json = """
    {
        "username": "alpha_dev", 
        "email": "developer@server.com",
        "age": 28,
        "devices": [
            {"device_name": "Mainframe-01", "ip_address": "10.0.0.4", "status": "Active"}
        ]
    }
    """
    clean_data = process_inbound_api_request(good_client_json)


    print("\n--- 3. Serializing Safe Outbound Data Payloads ---")
    if clean_data:
        # Mock database object output (with sensitive attributes like a hashed password)
        db_user_record = {
            "user_id": 9402,
            "username": clean_data.username,
            "email": clean_data.email,
            "hashed_password": "$2b$12$Z7xK18O93hJ9asdkj2389asdhjksh", # DO NOT SEND TO CLIENT
            "internal_sys_notes": "Premium cluster node tracking flagged"
        }
        
        # Serialize the user record cleanly using the output filtering schema
        outbound_payload = SafeUserResponse(**db_user_record)
        
        # Dump target clean model variables structure directly to browser layout 
        print(f"JSON Payload Sent to Client Browser:\n{outbound_payload.model_dump_json(indent=2)}")
