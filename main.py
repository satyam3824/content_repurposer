import streamlit as st
# Change this line:
# from repurposer import Repurposer
# To this:
from modules.repurposer import Repurposer
import os

# Set page configuration for a wider layout
st.set_page_config(layout="wide", page_title="AI Content Repurposing Tool")

# Initialize the Repurposer
try:
    repurposer = Repurposer()
except ValueError as e:
    st.error(f"Initialization Error: {e}")
    st.info("Please set your GOOGLE_API_KEY as an environment variable.")
    st.stop() # Stop the app if API key is not set

st.title("✨ AI Content Repurposing Tool")
st.markdown("Transform your long-form content into various formats effortlessly using Google Gemini and LangChain.")

# Sidebar for API Key input (optional, primarily for local testing/demonstration)
st.sidebar.header("Configuration")
st.sidebar.info("Your Google API Key should be set as an environment variable named `GOOGLE_API_KEY` for security. If you're running locally and haven't set it, you can paste it here for testing purposes.")
api_key_input = st.sidebar.text_input("Enter Google API Key (Optional)", type="password")

if api_key_input:
    os.environ["GOOGLE_API_KEY"] = api_key_input
    # Re-initialize repurposer if API key is provided via input
    try:
        repurposer = Repurposer()
        st.sidebar.success("API Key loaded successfully!")
    except ValueError as e:
        st.sidebar.error(f"Error loading API Key: {e}")


st.markdown("---")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Original Content")
    original_content = st.text_area(
        "Paste your content here:",
        height=300,
        placeholder="E.g., A detailed article about the benefits of meditation..."
    )

    st.header("Repurposing Options")
    repurpose_option = st.radio(
        "Choose a format to repurpose your content into:",
        ("Blog Post", "Tweet Thread", "Instagram Carousel", "LinkedIn Post (Coming Soon)", "Email Newsletter (Coming Soon)"),
        index=0 # Default to Blog Post
    )

    # Dynamic options based on selected repurposing format
    if repurpose_option == "Blog Post":
        st.subheader("Blog Post Settings")
        blog_target_audience = st.text_input("Target Audience", "general audience", help="Who is this blog post for?")
        blog_tone = st.selectbox("Tone", ["informative", "casual", "professional", "humorous", "academic"], index=0)
        blog_length = st.slider("Approximate Length (words)", 100, 1000, 500, step=50)
        repurpose_params = {
            "target_audience": blog_target_audience,
            "tone": blog_tone,
            "length": blog_length
        }
    elif repurpose_option == "Tweet Thread":
        st.subheader("Tweet Thread Settings")
        tweet_tone = st.selectbox("Tone", ["engaging", "informative", "witty", "casual"], index=0)
        repurpose_params = {"tone": tweet_tone}
    elif repurpose_option == "Instagram Carousel":
        st.subheader("Instagram Carousel Settings")
        carousel_tone = st.selectbox("Tone", ["visual and inspiring", "educational", "motivational", "fun"], index=0)
        carousel_num_slides = st.slider("Number of Slides", 3, 10, 5, step=1)
        repurpose_params = {
            "tone": carousel_tone,
            "num_slides": carousel_num_slides
        }
    else:
        st.info("This repurposing option is under development. Please choose another one.")
        repurpose_params = {} # No specific params for coming soon features

    st.markdown("---")
    generate_button = st.button("🚀 Generate Repurposed Content", use_container_width=True, type="primary")

with col2:
    st.header("Repurposed Output")
    output_placeholder = st.empty() # Placeholder for the output text area
    
    if generate_button:
        if not original_content.strip():
            output_placeholder.warning("Please enter some original content to repurpose.")
        elif repurpose_option in ["LinkedIn Post (Coming Soon)", "Email Newsletter (Coming Soon)"]:
            output_placeholder.info("This feature is coming soon! Please select an available option.")
        else:
            with st.spinner(f"Generating {repurpose_option.lower()}..."):
                try:
                    repurposed_content = repurposer.repurpose_content(
                        original_content,
                        repurpose_option,
                        **repurpose_params
                    )
                    output_placeholder.text_area(
                        "Your Repurposed Content:",
                        repurposed_content,
                        height=500,
                        key="repurposed_output" # Unique key for the text area
                    )
                except Exception as e:
                    output_placeholder.error(f"An error occurred during generation: {e}")
                    st.info("Please ensure your Google API Key is correctly set and you have an active internet connection.")

st.markdown("---")
st.markdown("Developed with ❤️ using LangChain, Google Gemini, and Streamlit.")
