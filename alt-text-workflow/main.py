from bedrock_agentcore.runtime import BedrockAgentCoreApp
from alt_text_langgraph import create_alt_text_workflow

app = BedrockAgentCoreApp()

@app.entrypoint
def agent_invocation(payload, context):
    response = create_alt_text_workflow().invoke(payload)
    return response

app.run()