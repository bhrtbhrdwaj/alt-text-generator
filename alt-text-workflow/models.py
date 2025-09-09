import boto3
import os
import json

def call_claude(model_id: str, conversation: list[dict]) -> str:
    client = boto3.client("bedrock-runtime", region_name=os.getenv("REGION_NAME"))

    response = client.converse(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.8},
    )

    return response["output"]["message"]["content"][0]["text"]
