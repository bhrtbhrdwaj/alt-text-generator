import boto3
import json
import base64
import os
from dotenv import load_dotenv

load_dotenv()


def invoke_agent_runtime(request):
    print(f"Invoking agent runtime with request: {request}")
    client = boto3.client("bedrock-agentcore", region_name=os.environ.get("DEFAULT_REGION", "us-east-1"))
    request = json.dumps(request).encode("utf-8")
    
    response = client.invoke_agent_runtime(
        agentRuntimeArn=os.environ.get("AGENT_RUNTIME_ARN"),
        qualifier=os.environ.get("AGENT_API", "DEFAULT"),
        payload=request,
    )
    stream = response["response"]

    response_content = ""
    for chunk in stream:
        if isinstance(chunk, (bytes, bytearray)):
            response_content += chunk.decode("utf-8")
        else:
            response_content += str(chunk)

    if response_content:
        try:
            response_json = json.loads(response_content)
            print(f"Final response content: {response_json}")
            return response_json
        except Exception as e:
            print(f"Error parsing JSON response: {str(e)}")
            return {
                "generated_alt_text": response_content,
                "complexity_level": "Unknown",
                "complexity_reasoning": "Response was not in JSON format",
                "feedback_history": [],
                "revision_count": 0,
                "max_revisions": 3,
                "waiting_for_feedback": True,
            }
    else:
        return {"error": "No content in response chunks"}