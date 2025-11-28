import streamlit as st
import os
import pandas as pd
from src.folder_manager import FolderManager
from src.content_gen import ContentGenerator
from src.ppt_gen import PPTGenerator

# Page Config
st.set_page_config(page_title="Advanced Academic PPT Generator", layout="wide")

# Session State Initialization
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'project_path' not in st.session_state:
    st.session_state.project_path = None
if 'slides_data' not in st.session_state:
    st.session_state.slides_data = None
if 'topic' not in st.session_state:
    st.session_state.topic = ""

# Sidebar
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password", value=os.getenv("GOOGLE_API_KEY", ""))

# Model Selection
text_model = st.sidebar.selectbox(
    "Text Generation Model",
    ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
    index=0
)

image_model = st.sidebar.selectbox(
    "Image Generation Model",
    ["imagen-4.0-generate-001", "imagen-4.0-fast-generate-001", "imagen-3.0-generate-001", "dall-e-3 (Placeholder)", "None"],
    index=0
)

# Language Selection
language = st.sidebar.selectbox(
    "Presentation Language",
    ["Korean", "English", "Mixed (Korean/English)"],
    index=0
)

# Initialize Classes
folder_manager = FolderManager()
content_gen = None
if api_key:
    try:
        content_gen = ContentGenerator(api_key, text_model_name=text_model, image_model_name=image_model)
    except Exception as e:
        st.sidebar.error(f"Invalid API Key: {e}")

ppt_gen = PPTGenerator()

# Main Title
st.title("Advanced Academic PPT Generator")

# Progress Bar
steps = ["1. Setup", "2. Draft", "3. Edit", "4. Generate"]
st.progress((st.session_state.current_step - 1) / 3)
st.write(f"**Current Step: {steps[st.session_state.current_step - 1]}**")

# --- Step 1: Project Setup & File Upload ---
if st.session_state.current_step == 1:
    st.header("Step 1: Project Setup")
    
    topic = st.text_input("Presentation Topic", value=st.session_state.topic)
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_files = st.file_uploader("Upload Reference Materials (Text, PDF, Images)", accept_multiple_files=True)
    with col2:
        manual_text = st.text_area("Manual Content Input (Optional)", height=150, placeholder="Paste additional text or notes here...")
    
    # Slide Count Selection
    slide_count = st.slider("Target Number of Slides", min_value=1, max_value=50, value=10)
    
    if st.button("Create Project & Proceed"):
        if not topic:
            st.error("Please enter a topic.")
        elif not api_key:
            st.error("Please enter a Gemini API Key in the sidebar.")
        else:
            # Create Project Structure
            project_path = folder_manager.create_project_structure(topic)
            st.session_state.project_path = project_path
            st.session_state.topic = topic
            st.session_state.language = language 
            st.session_state.slide_count = slide_count # Store slide count
            
            # Save Uploaded Files
            input_folder = os.path.join(project_path, "input")
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    folder_manager.save_uploaded_file(uploaded_file, input_folder)
            
            # Save Manual Text
            if manual_text:
                with open(os.path.join(input_folder, "manual_input.txt"), "w", encoding="utf-8") as f:
                    f.write(manual_text)
            
            st.success(f"Project created at: {project_path}")
            st.session_state.current_step = 2
            st.rerun()

# --- Step 2: AI Draft Generation ---
elif st.session_state.current_step == 2:
    st.header("Step 2: AI Draft Generation")
    
    st.info(f"Topic: {st.session_state.topic} | Language: {st.session_state.get('language', 'Korean')} | Slides: {st.session_state.get('slide_count', 10)}")
    st.write("Click below to analyze materials and generate a slide draft.")
    
    if st.button("Generate Draft"):
        with st.spinner("Analyzing materials and generating structure..."):
            # Read materials (simplified for text files for now)
            input_folder = os.path.join(st.session_state.project_path, "input")
            materials_content = ""
            for filename in os.listdir(input_folder):
                file_path = os.path.join(input_folder, filename)
                try:
                    # Basic text reading, can be expanded for PDF/Images
                    if filename.endswith(".txt") or filename.endswith(".md"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            materials_content += f.read() + "\n\n"
                except Exception as e:
                    st.warning(f"Could not read {filename}: {e}")
            
            if not materials_content:
                materials_content = "No specific materials provided. Generate based on general knowledge."

            # Generate Structure
            slides_data = content_gen.analyze_and_generate_structure(
                st.session_state.topic, 
                materials_content,
                language=st.session_state.get('language', 'Korean'),
                slide_count=st.session_state.get('slide_count', 10)
            )
            
            if slides_data:
                st.session_state.slides_data = slides_data
                # Save to config
                config_path = os.path.join(st.session_state.project_path, "config", "slides.json")
                folder_manager.save_json(slides_data, config_path)
                
                st.success("Draft generated!")
                st.session_state.current_step = 3
                st.rerun()
            else:
                st.error("Failed to generate draft. Please try again.")

# --- Step 3: Edit Slides ---
elif st.session_state.current_step == 3:
    st.header("Step 3: Review & Edit")
    
    if st.session_state.slides_data:
        st.write("Expand each slide to edit its details.")
        
        # Form to hold all inputs
        with st.form("edit_slides_form"):
            updated_slides = []
            for i, slide in enumerate(st.session_state.slides_data['slides']):
                with st.expander(f"Slide {slide['id']}: {slide.get('title', 'Untitled')}", expanded=(i==0)):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        new_title = st.text_input(f"Title", value=slide.get('title', ''), key=f"title_{i}")
                        new_content = st.text_area(f"Content", value=slide.get('content', ''), height=150, key=f"content_{i}")
                        new_prompt = st.text_area(f"Image Prompt", value=slide.get('image_prompt', ''), height=100, key=f"prompt_{i}")
                    
                    with col2:
                        new_layout = st.selectbox(
                            "Layout",
                            options=["Title_Image_Right", "Title_Image_Left", "Title_Only", "Two_Column"],
                            index=["Title_Image_Right", "Title_Image_Left", "Title_Only", "Two_Column"].index(slide.get('layout', 'Title_Image_Right')) if slide.get('layout') in ["Title_Image_Right", "Title_Image_Left", "Title_Only", "Two_Column"] else 0,
                            key=f"layout_{i}"
                        )
                        st.caption(f"Slide ID: {slide['id']}")

                    # Update slide object (this logic runs on re-run, but we collect in form submit)
                    # However, inside a form, we need to handle the submit action to update the state.
                    # We will reconstruct the list on submit.
            
            submitted = st.form_submit_button("Save & Proceed")
            
            if submitted:
                # Reconstruct slides data from session state widgets
                new_slides_list = []
                for i, old_slide in enumerate(st.session_state.slides_data['slides']):
                    updated_slide = old_slide.copy()
                    updated_slide['title'] = st.session_state[f"title_{i}"]
                    updated_slide['content'] = st.session_state[f"content_{i}"]
                    updated_slide['image_prompt'] = st.session_state[f"prompt_{i}"]
                    updated_slide['layout'] = st.session_state[f"layout_{i}"]
                    new_slides_list.append(updated_slide)
                
                st.session_state.slides_data['slides'] = new_slides_list
                
                # Save to file
                config_path = os.path.join(st.session_state.project_path, "config", "slides.json")
                folder_manager.save_json(st.session_state.slides_data, config_path)
                
                st.success("Changes saved!")
                st.session_state.current_step = 4
                st.rerun()
            
    else:
        st.error("No slide data found. Go back to Step 2.")
        if st.button("Back"):
            st.session_state.current_step = 2
            st.rerun()

# --- Step 4: Generate PPT ---
elif st.session_state.current_step == 4:
    st.header("Step 4: Generate Presentation")
    
    st.write("Ready to generate images and final PowerPoint.")
    
    if st.button("Start Generation"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_container = st.expander("Generation Logs", expanded=True)
        
        images_folder = os.path.join(st.session_state.project_path, "images")
        output_folder = os.path.join(st.session_state.project_path, "output")
        total_slides = len(st.session_state.slides_data['slides'])
        
        # 1. Generate Images
        for i, slide in enumerate(st.session_state.slides_data['slides']):
            status_text.text(f"Generating image for Slide {slide['id']}...")
            if slide.get('image_prompt'):
                img_path = os.path.join(images_folder, f"slide_{slide['id']}.png")
                success, msg = content_gen.generate_image(slide['image_prompt'], img_path)
                if success:
                    log_container.success(f"Slide {slide['id']}: Image generated.")
                else:
                    log_container.error(f"Slide {slide['id']}: Failed - {msg}")
            progress_bar.progress((i + 1) / (total_slides * 2))
            
        # 2. Generate PPT
        status_text.text("Assembling PowerPoint...")
        output_path = os.path.join(output_folder, "presentation.pptx")
        ppt_gen.generate_ppt(st.session_state.slides_data, images_folder, output_path)
        progress_bar.progress(1.0)
        
        status_text.text("Done!")
        st.success(f"Presentation generated at: {output_path}")
        
        # Download Button
        with open(output_path, "rb") as f:
            st.download_button(
                label="Download PPT",
                data=f,
                file_name="presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
            
    if st.button("Start New Project"):
        st.session_state.current_step = 1
        st.session_state.topic = ""
        st.session_state.project_path = None
        st.session_state.slides_data = None
        st.rerun()
