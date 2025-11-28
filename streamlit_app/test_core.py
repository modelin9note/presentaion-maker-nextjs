import os
import shutil
from src.folder_manager import FolderManager
from src.content_gen import ContentGenerator
from src.ppt_gen import PPTGenerator

def test_core_logic():
    print("Testing Core Logic...")
    
    # 1. Test FolderManager
    print("\n[1] Testing FolderManager...")
    fm = FolderManager("test_projects")
    project_path = fm.create_project_structure("Test Topic")
    print(f"Project created at: {project_path}")
    
    assert os.path.exists(os.path.join(project_path, "input"))
    assert os.path.exists(os.path.join(project_path, "config"))
    assert os.path.exists(os.path.join(project_path, "images"))
    assert os.path.exists(os.path.join(project_path, "output"))
    print("Folder structure verified.")

    # 2. Test ContentGenerator (Mocking API for safety if key not present, but trying real if env var exists)
    print("\n[2] Testing ContentGenerator...")
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        cg = ContentGenerator(api_key)
        # Mock response to save tokens/time for this test, or use a simple prompt
        # For this test, we'll manually construct the data to test the flow
        slides_data = {
            "slides": [
                {
                    "id": 1,
                    "title": "Test Slide 1",
                    "content": "Content for slide 1",
                    "image_prompt": "A blue circle",
                    "layout": "Title_Image_Right"
                },
                {
                    "id": 2,
                    "title": "Test Slide 2",
                    "content": "Content for slide 2",
                    "layout": "Title_Only"
                }
            ]
        }
        print("ContentGenerator initialized (Skipping actual API call for test speed).")
        
        # Test Image Gen (Placeholder)
        img_path = os.path.join(project_path, "images", "slide_1.png")
        cg.generate_image("A blue circle", img_path)
        assert os.path.exists(img_path)
        print("Image generation (placeholder) verified.")
        
    else:
        print("Skipping ContentGenerator test (No API Key found).")
        slides_data = {
            "slides": [
                {
                    "id": 1,
                    "title": "Test Slide 1",
                    "content": "Content for slide 1",
                    "image_prompt": "A blue circle",
                    "layout": "Title_Image_Right"
                }
            ]
        }
        # Manually create dummy image
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = 'red')
        os.makedirs(os.path.join(project_path, "images"), exist_ok=True)
        img.save(os.path.join(project_path, "images", "slide_1.png"))

    # 3. Test PPTGenerator
    print("\n[3] Testing PPTGenerator...")
    pg = PPTGenerator()
    output_path = os.path.join(project_path, "output", "test_pres.pptx")
    pg.generate_ppt(slides_data, os.path.join(project_path, "images"), output_path)
    
    assert os.path.exists(output_path)
    print(f"PPT generated at: {output_path}")
    print("PPTGenerator verified.")
    
    # Cleanup
    # shutil.rmtree("test_projects")
    print("\nTest Complete. 'test_projects' folder left for inspection.")

if __name__ == "__main__":
    test_core_logic()
