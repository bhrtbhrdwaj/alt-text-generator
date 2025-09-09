import streamlit as st
import requests
import base64
from PIL import Image
import io
import json
from agent_core_runtime import invoke_agent_runtime

st.set_page_config(
    page_title="Alt-Text Generator with Feedback",
    page_icon="🖼️",
    layout="wide"
)

def init_session_state():
    if 'api_response' not in st.session_state:
        st.session_state.api_response = None
    if 'current_image_hash' not in st.session_state:
        st.session_state.current_image_hash = None
    if 'feedback_given' not in st.session_state:
        st.session_state.feedback_given = False
    if 'feedback_text' not in st.session_state:
        st.session_state.feedback_text = ""

def image_to_base64(image_file):
    """Convert uploaded image to base64 string with original format and data URI prefix"""
    try:
        image = Image.open(image_file)
        format = image.format  # e.g., 'PNG', 'JPEG'
        mime_type = f"image/{format.lower()}" if format else "image/jpeg"

        # Convert to RGB only if needed for JPEG
        if format == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')

        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:{mime_type};base64,{img_base64}"
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None
        
def make_api_call(payload):
    """Make API call to alt-text generation service"""
    try:
        return invoke_agent_runtime(payload)
    except Exception as e:
        st.error(f"Agent Runtime call failed: {str(e)}")
        print(f"Error details: {str(e)}")
        return None

def reset_state_for_new_image():
    """Reset session state when a new image is uploaded"""
    st.session_state.api_response = None
    st.session_state.feedback_given = False

def main():
    init_session_state()
    
    st.title("🖼️ Alt-Text Generator with Feedback Loop")
    st.markdown("Upload an image and/or provide a description to generate alt-text with iterative feedback.")
    
    with st.sidebar:
        st.markdown("### How it works:")
        st.markdown("""
        1. Upload an image and/or provide description
        2. Get initial alt-text generation
        3. Provide feedback to improve the result
        4. Continue until you're satisfied (max 3 revisions)
        """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Input")
        
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a PNG or JPEG image"
        )
        
        if uploaded_file is not None:
            current_hash = hash(uploaded_file.getvalue())
            if st.session_state.current_image_hash != current_hash:
                st.session_state.current_image_hash = current_hash
                reset_state_for_new_image()
            
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        user_input = st.text_area(
            "Image Description (Optional)",
            height=100,
            help="Provide a description of the image or additional context"
        )
        
        if st.button("🚀 Generate Alt-Text", type="primary"):
            if uploaded_file is None and not user_input.strip():
                st.error("Please upload an image or provide a description!")
            else:
                payload = {
                    "image_data": None,
                    "user_input": user_input.strip() if user_input else "",
                    "feedback_history": [],
                    "revision_count": 0,
                    "max_revisions": 3,
                    "waiting_for_feedback": False
                }
                
                if uploaded_file is not None:
                    with st.spinner("Processing image..."):
                        base64_image = image_to_base64(uploaded_file)
                        if base64_image:
                            payload["image_data"] = base64_image
                        else:
                            st.error("Failed to process image")
                            return
                
                with st.spinner("Generating alt-text..."):
                    response = make_api_call(payload)
                    if response:
                        st.session_state.api_response = response
                        st.session_state.feedback_given = False
                        
    
    with col2:
        st.header("📤 Results")
        
        if st.session_state.api_response:
            response = st.session_state.api_response
            
            st.subheader("Generated Alt-Text")
            st.success(response.get("generated_alt_text", ""))
            
            col2a, col2b = st.columns(2)
            with col2a:
                complexity = response.get("complexity_level", "Unknown")
                st.metric("Complexity Level", complexity)
            with col2b:
                revision_count = response.get("revision_count", 0)
                max_revisions = response.get("max_revisions", 3)
                st.metric("Revisions", f"{revision_count}/{max_revisions}")
            
            if response.get("complexity_reasoning"):
                with st.expander("💡 Complexity Reasoning"):
                    st.write(response["complexity_reasoning"])
            
            if response.get("feedback_history"):
                with st.expander("📝 Feedback History"):
                    for i, feedback in enumerate(response["feedback_history"], 1):
                        st.write(f"**Feedback {i}:** {feedback}")
            
            if (response.get("waiting_for_feedback", False) and 
                response.get("revision_count", 0) < response.get("max_revisions", 3)):
                
                st.markdown("---")
                st.subheader("💬 Provide Feedback")
                
                feedback_text = st.text_area(
                    "How can we improve this alt-text?",
                    height=100,
                    help="Provide specific feedback on what should be changed or improved"
                )
                
                col_feedback1, col_feedback2 = st.columns(2)
                
                with col_feedback1:
                    if st.button("✅ Submit Feedback", type="primary"):
                        if feedback_text.strip():
                            feedback_payload = {
                                "image_data": response.get("image_data"),
                                "user_input": feedback_text.strip(),
                                "complexity_level": response.get("complexity_level"),
                                "complexity_reasoning": response.get("complexity_reasoning"),
                                "generated_alt_text": response.get("generated_alt_text"),
                                "feedback_history": response.get("feedback_history", []),
                                "revision_count": response.get("revision_count", 0),
                                "max_revisions": response.get("max_revisions", 3),
                                "waiting_for_feedback": True
                            }
                            
                            with st.spinner("Processing feedback..."):
                                new_response = None
                                if st.session_state.feedback_text != feedback_text.strip():
                                    new_response = make_api_call(feedback_payload)
                                if new_response:
                                    st.session_state.api_response = new_response
                                    st.session_state.feedback_given = True
                                    st.session_state.feedback_text = feedback_text.strip()
                                    st.rerun()
                                    
                        else:
                            st.error("Please provide feedback before submitting!")
            
            elif response.get("revision_count", 0) >= response.get("max_revisions", 3):
                st.info("Maximum revisions reached. You can start over with a new image.")
        
        else:
            st.info("Upload an image or provide a description to get started!")
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Alt-Text Generator with Feedback Loop | Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()