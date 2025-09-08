from typing import TypedDict, Literal, Optional, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import uuid
from models import call_claude
import base64 

load_dotenv()

complexity_model = os.getenv("LIGHT_WEIGHT_MODEL", "")
generation_model = os.getenv("DEFAULT_MODEL", "")


class AltTextState(TypedDict):
    image_data: Optional[str] = None
    user_input: Optional[str] = None
    complexity_level: Optional[Literal["Simple", "Moderate", "Complex"]] = None
    complexity_reasoning: Optional[str] = None
    generated_alt_text: Optional[str] = None
    feedback_history: Optional[List[str]] = None
    revision_count: Optional[int] = 0
    max_revisions: Optional[int] = 3
    waiting_for_feedback: Optional[bool] = None


def ensure_state_defaults(state: AltTextState) -> AltTextState:
    if "revision_count" not in state:
        state["revision_count"] = 0
    if "max_revisions" not in state:
        state["max_revisions"] = 3
    if "feedback_history" not in state:
        state["feedback_history"] = []
    return state

def routing_node(state: AltTextState) -> AltTextState:
    """ Dummy node """
    return ensure_state_defaults(state)

def get_messages(state: AltTextState, complexity_prompt: str) -> list[dict]:
    messages = []
    image_data = state.get("image_data")
    if image_data and image_data.startswith("data:image"):
        image_base64 = image_data.split(",")[1]
        image_bytes = base64.b64decode(image_base64)

        messages.append({
            "role": "user",
            "content": [{
            "image": {
                "format": image_data.split(";")[0].split("/")[1],
                "source": {
                    "bytes": image_bytes
                }
            }
        }, {
                    "text": f"{complexity_prompt}\n\nImage description: {state.get('user_input', 'No image description provided')}"
                }],
        })
    else:
        messages.append({
            "role": "user",
            "content": [{"text": f"{complexity_prompt}\n\nImage description: {state.get('user_input', 'No image description provided')}"}],
        })
    return messages

def complexity_analysis_node(state: AltTextState) -> AltTextState:
    """Stage 1: Analyze the complexity of the image content"""
    print("🔍 Stage 1: Analyzing image complexity...")
    
    complexity_prompt = """
    You are a lightweight model specialized in categorizing image complexity for alt-text generation.
    
    Analyze the provided content and categorize it into one of three complexity levels:
    
    **Simple**: Basic images with minimal elements (e.g., single object, simple scene, clear subject)
    **Moderate**: Images with multiple elements but clear structure (e.g., 2-3 main objects, straightforward relationships)
    **Complex**: Images with many elements, intricate details, or complex relationships (e.g., detailed scenes, multiple people, complex data visualizations)

    Provide your analysis strictly in below format:
    COMPLEXITY: [Simple/Moderate/Complex]
    REASONING: [Brief explanation of why this complexity level was chosen]
    """

    messages = get_messages(state, complexity_prompt)

    response_text = call_claude(complexity_model, messages)
    print(f"Complexity Response: {response_text}")
    lines = response_text.split('\n')
    complexity_level = None
    reasoning = None
    
    for line in lines:
        if line.startswith('COMPLEXITY:'):
            complexity_level = line.split(':', 1)[1].strip()
        elif line.startswith('REASONING:'):
            reasoning = line.split(':', 1)[1].strip()
    
    state["complexity_level"] = complexity_level
    state["complexity_reasoning"] = reasoning
    
    print(f"   Complexity Level: {complexity_level}")
    print(f"   Reasoning: {reasoning}")
    
    return state

def alt_text_generation_node(state: AltTextState) -> AltTextState:
    """Stage 2: Generate alt-text based on complexity level"""
    print(f"✏️  Stage 2: Generating alt-text for {state['complexity_level']} complexity...")
    
    complexity_guidelines = {
        "Simple": """
        For SIMPLE images, create concise alt-text (1-2 sentences, max 125 characters):
        - Focus on the main subject/object
        - Use clear, direct language
        - Avoid unnecessary details
        - Example: "A red apple on a white plate"
        """,
        
        "Moderate": """
        For MODERATE images, create descriptive alt-text (2-3 sentences, max 200 characters):
        - Describe main elements and their relationships
        - Include relevant context
        - Maintain logical flow
        - Example: "Three business people in suits reviewing documents at a conference table in a modern office"
        """,
        
        "Complex": """
        For COMPLEX images, create comprehensive alt-text (3-4 sentences, max 300 characters):
        - Describe the overall scene first
        - Detail key elements and their interactions
        - Include spatial relationships and context
        - Prioritize information hierarchy
        - Example: "A bustling farmers market with multiple vendor stalls displaying colorful produce. Customers browse vegetables in the foreground while vendors arrange items in the background under white canopy tents"
        """
    }
    
    generation_prompt = f"""
    You are an expert alt-text generator specializing in creating accessible image descriptions.
    
    {complexity_guidelines.get(state['complexity_level'], complexity_guidelines['Moderate'])}
    
    ACCESSIBILITY GUIDELINES:
    - Start with the most important information
    - Use specific, concrete language
    - Avoid subjective interpretations
    - Don't start with "Image of" or "Picture of"
    - Consider the context and purpose

    Provide your alt-text strictly in below format:
    ALT-TEXT: [Your generated alt-text here]
    """

    messages = get_messages(state, generation_prompt)

    alt_text = call_claude(generation_model, messages)
    print(f"Alt-text Response: {alt_text}")
    
    if alt_text.startswith('ALT-TEXT:'):
        alt_text = alt_text.split(':', 1)[1].strip()
    
    if alt_text:
        alt_text = alt_text[0].upper() + alt_text[1:]
    
    state["generated_alt_text"] = alt_text
    state["waiting_for_feedback"] = True
    state["image_data"] = None
    
    print(f"   Generated Alt-text: {alt_text}")
    print(f"   Character count: {len(alt_text)}")
    print("👤 Ready for user feedback...")
    
    return state

def revision_node(state: AltTextState) -> AltTextState:
    """Handle revision based on user feedback"""
    print(f"🔄 Revision #{state['revision_count'] + 1}: Incorporating user feedback...")
    
    feedback_context = ""
    if state.get("feedback_history"):
        feedback_context = "\n".join([f"- {fb}" for fb in state["feedback_history"]])
    
    revision_prompt = f"""
    Revise the alt-text based on the user feedback:
    
    ORIGINAL ALT-TEXT: "{state['generated_alt_text']}"
    COMPLEXITY LEVEL: {state['complexity_level']}
    USER FEEDBACK: "{state['user_input']}"
    
    Previous feedback (if any):
    {feedback_context}
    
    REQUIREMENTS:
    - Address the specific feedback provided
    - Maintain accessibility standards
    - Keep appropriate for {state['complexity_level']} complexity level
    - Ensure clarity and usefulness for screen readers

    Provide your revised alt-text strictly in below format:
    ALT-TEXT: [Your improved alt-text here]
    """
    
    response = call_claude(generation_model, [{"role": "user", "content": [{"text": revision_prompt}]}])
    print(f"Revision Response: {response}")
    revised_text = response.strip()

    if revised_text.startswith('ALT-TEXT:'):
        revised_text = revised_text.split(':', 1)[1].strip()
    
    if revised_text:
        revised_text = revised_text[0].upper() + revised_text[1:]
    
    feedback_history = state.get("feedback_history", [])
    feedback_history.append(state["user_input"])
    
    state["generated_alt_text"] = revised_text
    state["revision_count"] = state["revision_count"] + 1
    state["feedback_history"] = feedback_history
    state["user_input"] = None
    state["waiting_for_feedback"] = True
    
    print(f"   Revised Alt-text: {revised_text}")
    print(f"   Character count: {len(revised_text)}")
    print("👤 Ready for user feedback...")
    
    return state

def completed_node(state: AltTextState) -> AltTextState:
    state["user_input"] = None
    state["waiting_for_feedback"] = False
    
    return state

def feedback_routing(state: AltTextState) -> Literal["complexity_analysis", "revision", "complete"]:
    """Route based on feedback state"""
    if not state.get("waiting_for_feedback"):
        return "complexity_analysis"

    if state.get("waiting_for_feedback") and state.get("user_input", "") == "approve":
        print(f"✅ User approved the alt-text.")
        return "complete"
    
    if state["revision_count"] >= state["max_revisions"]:
        print(f"⚠️ Maximum revisions ({state['max_revisions']}) reached. Can't review now")
        return "complete"

    return "revision"

def create_alt_text_workflow():
    workflow = StateGraph(AltTextState)
    
    workflow.add_node("routing", routing_node)
    workflow.add_node("complexity_analysis", complexity_analysis_node)
    workflow.add_node("alt_text_generation", alt_text_generation_node)
    workflow.add_node("revision", revision_node)
    workflow.add_node("complete", completed_node)

    workflow.set_entry_point("routing")

    workflow.add_conditional_edges(
        "routing",
        feedback_routing,
        {
            "complexity_analysis": "complexity_analysis",
            "revision": "revision",
            "complete": "complete",}
    )

    workflow.add_edge("complexity_analysis", "alt_text_generation")
    workflow.add_edge("alt_text_generation", END)
    workflow.add_edge("revision", END)
    workflow.add_edge("complete", END)

    return workflow.compile()

