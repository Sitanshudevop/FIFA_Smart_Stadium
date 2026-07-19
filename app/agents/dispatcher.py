from google import genai
from google.genai import types
import os
from pydantic import BaseModel
from app.agents.tools import find_optimal_volunteer
from app.models.schemas import DispatchPayload
from fastapi import APIRouter

router = APIRouter(prefix="/dispatch", tags=["dispatcher"])

class DispatchRequest(BaseModel):
    incident: str

@router.post("/", response_model=DispatchPayload)
async def dispatch_incident(req: DispatchRequest):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "mock_key"))
    
    prompt = f"Assign a volunteer to handle this incident: {req.incident}"
    
    # Send the initial request providing the tool
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[prompt],
        config=types.GenerateContentConfig(
            tools=[find_optimal_volunteer],
            temperature=0.1
        )
    )
    
    # Check if function call is requested
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    
    if response.function_calls:
        contents.append(response.candidates[0].content)
        call = response.function_calls[0]
        
        if call.name == "find_optimal_volunteer":
            tool_res = find_optimal_volunteer(**call.args)
            contents.append(
                types.Content(role="tool", parts=[
                    types.Part.from_function_response(name=call.name, response={"result": tool_res}, id=call.id)
                ])
            )
            
            # Final resolution with schema enforcement
            final_res = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DispatchPayload,
                )
            )
            return final_res.parsed
            
    # If no tool was called, still attempt to return structured response
    final_res = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DispatchPayload,
        )
    )
    return final_res.parsed
