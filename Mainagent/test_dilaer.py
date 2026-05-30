import asyncio
from livekit import api
from livekit.protocol.sip import (
    CreateSIPOutboundTrunkRequest, 
    SIPOutboundTrunkInfo,
    CreateSIPParticipantRequest
)

async def main():
    # Docker Compose --dev mode credentials
    livekit_url = "http://localhost:7880"
    api_key = "devkey"
    api_secret = "secret"

    # Vobiz SIP Trunk Details
    sip_address = "449caee4.sip.vobiz.ai"
    auth_username = "jon"
    auth_password = "Smr123bunny$#"
    
    # ---------------------------------------------------------
    # Update with your target test number
    # ---------------------------------------------------------
    vobiz_caller_id = "+918065480756"    
    target_destination = "+919032812294" # <-- Replace with the number you are dialing
    # ---------------------------------------------------------

    async with api.LiveKitAPI(livekit_url, api_key=api_key, api_secret=api_secret) as lkapi:
        
        print(f"1. Configuring Vobiz SIP Trunk with Caller ID: {vobiz_caller_id}...")
        
        trunk_info = SIPOutboundTrunkInfo(
            name="vobiz-outbound",
            address=sip_address,
            numbers=[vobiz_caller_id], 
            auth_username=auth_username,
            auth_password=auth_password
        )
        
        trunk_req = CreateSIPOutboundTrunkRequest(trunk=trunk_info)
        
        # Uses the updated method to prevent deprecation errors
        trunk = await lkapi.sip.create_outbound_trunk(trunk_req)
        
        print(f"Trunk ready with ID: {trunk.sip_trunk_id}")
        print(f"2. Initiating outbound call to {target_destination}...")
        
        part_req = CreateSIPParticipantRequest(
            sip_trunk_id=trunk.sip_trunk_id,
            sip_call_to=target_destination,
            room_name="outbound-test-room",
            participant_identity="customer-phone"
        )
        
        participant = await lkapi.sip.create_sip_participant(part_req)

        print("Call successfully dispatched!")
        print(f"Participant ID: {participant.participant_id}")

if __name__ == "__main__":
    asyncio.run(main())