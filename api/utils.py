import os
import json
import traceback
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import requests
import base64
import io
from pptx import Presentation
from pptx.util import Inches, Pt

class ContentGenerator:
    def __init__(self, api_key, text_model_name='gemini-2.0-flash-exp', image_model_name='imagen-4.0-generate-001'):
        self.api_key = api_key
        self.text_model_name = text_model_name
        self.image_model_name = image_model_name
        
        if not api_key:
            raise ValueError("API Key is required")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.text_model_name)

    def analyze_and_generate_structure(self, topic, materials_content, language="Korean", slide_count=10):
        prompt = f"""
        You are an expert academic presentation designer.
        Create a structured presentation plan for the topic: "{topic}".
        
        Requirements:
        1. Language: The content MUST be written in {language}.
        2. Slide Count: Generate exactly {slide_count} slides.
        
        Here is the content from the provided materials:
        {materials_content[:15000]}
        
        Generate a JSON response with the following structure:
        {{
            "slides": [
                {{
                    "id": 1,
                    "title": "Slide Title (in {language})",
                    "content": "Bullet points or text content for the slide (in {language}). Keep it concise.",
                    "image_prompt": "A detailed description for an AI image generator to create a relevant image (Always in English).",
                    "layout": "Title_Image_Right"  # Options: Title_Image_Right, Title_Image_Left, Title_Only, Two_Column
                }},
                ...
            ]
        }}
        
        Ensure the presentation has a logical flow: Introduction, Core Concepts, Analysis/Details, Conclusion.
        The "layout" field must be one of the specified options.
        Return ONLY the JSON string, no markdown formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text)
        except Exception as e:
            print(f"Error generating structure: {e}")
            return None

    def generate_image(self, prompt):
        """
        Generates an image and returns base64 string.
        Returns: (success: bool, data: str, message: str)
        """
        print(f"Generating image with model: {self.image_model_name} for prompt: {prompt}")
        
        if 'imagen' in self.image_model_name:
            return self._generate_image_rest(prompt)
        else:
            return self._create_placeholder_image(prompt)

    def _generate_image_rest(self, prompt):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.image_model_name}:predict?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "instances": [{"prompt": prompt}],
            "parameters": {"sampleCount": 1, "aspectRatio": "16:9"}
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if "predictions" in result and len(result["predictions"]) > 0:
                b64_image = result["predictions"][0]["bytesBase64Encoded"]
                return True, b64_image, "Success"
            else:
                return False, None, f"No image data: {result}"
        except Exception as e:
            print(f"Error generating image: {e}")
            return False, None, str(e)

    def _create_placeholder_image(self, prompt):
        try:
            img = Image.new('RGB', (1280, 720), color = (73, 109, 137))
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.load_default()
            except:
                pass
            
            d.text((50, 300), f"Prompt: {prompt[:50]}...", fill=(255, 255, 0))
            
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return True, img_str, "Placeholder Created"
        except Exception as e:
            return False, None, str(e)

class PPTGenerator:
    def generate_ppt(self, slides_data):
        """
        Generates PPTX and returns bytes.
        """
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        
        for slide_info in slides_data['slides']:
            layout_type = slide_info.get('layout', 'Title_Only')
            slide_layout = prs.slide_layouts[5] 
            slide = prs.slides.add_slide(slide_layout)
            
            title = slide.shapes.title
            title.text = slide_info.get('title', 'No Title')
            title.left = Inches(0.5)
            title.top = Inches(0.5)
            title.width = Inches(12.333)
            title.height = Inches(1.0)
            
            content = slide_info.get('content', '')
            image_data = slide_info.get('image_base64') # Expecting base64 string
            
            if layout_type == 'Title_Only':
                self._add_text(slide, content, Inches(1), Inches(2), Inches(11.333), Inches(5))
            
            elif layout_type == 'Title_Image_Right':
                self._add_text(slide, content, Inches(0.5), Inches(2), Inches(6), Inches(5))
                if image_data:
                    self._add_image(slide, image_data, Inches(7), Inches(2), width=Inches(5.8))
            
            elif layout_type == 'Title_Image_Left':
                if image_data:
                    self._add_image(slide, image_data, Inches(0.5), Inches(2), width=Inches(5.8))
                self._add_text(slide, content, Inches(6.8), Inches(2), Inches(6), Inches(5))
            
            elif layout_type == 'Two_Column':
                self._add_text(slide, content, Inches(0.5), Inches(2), Inches(6), Inches(5))
                self._add_text(slide, " ", Inches(6.8), Inches(2), Inches(6), Inches(5))
            
            else:
                self._add_text(slide, content, Inches(1), Inches(2), Inches(11.333), Inches(5))

        output = io.BytesIO()
        prs.save(output)
        output.seek(0)
        return output

    def _add_text(self, slide, text, left, top, width, height):
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.text = text

    def _add_image(self, slide, b64_data, left, top, width=None, height=None):
        try:
            image_bytes = base64.b64decode(b64_data)
            image_stream = io.BytesIO(image_bytes)
            slide.shapes.add_picture(image_stream, left, top, width=width, height=height)
        except Exception as e:
            print(f"Error adding image: {e}")
