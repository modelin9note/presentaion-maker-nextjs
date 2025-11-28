import os
import json
import traceback
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

import requests
import base64

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
        """
        Analyzes the topic and materials to generate a JSON structure for the presentation.
        """
        prompt = f"""
        You are an expert academic presentation designer.
        Create a structured presentation plan for the topic: "{topic}".
        
        Requirements:
        1. Language: The content MUST be written in {language}.
        2. Slide Count: Generate exactly {slide_count} slides.
        
        Here is the content from the provided materials:
        {materials_content[:15000]}  # Truncate to avoid token limits
        
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
            # Clean up potential markdown code blocks
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text)
        except Exception as e:
            print(f"Error generating structure: {e}")
            return None

    def generate_image(self, prompt, output_path):
        """
        Generates an image using the selected model.
        Returns: (success: bool, message: str)
        """
        print(f"Generating image with model: {self.image_model_name} for prompt: {prompt}")
        
        if 'imagen' in self.image_model_name:
            return self._generate_image_rest(prompt, output_path)
        
        else:
            # Placeholder or other models
            self._create_placeholder_image(prompt, output_path)
            return True, "Placeholder used"

    def _generate_image_rest(self, prompt, output_path):
        """
        Generates an image using the Gemini API REST endpoint for Imagen models.
        """
        print(f"Generating image via REST API for prompt: {prompt} using model: {self.image_model_name}")
        start_time = time.time()
        
        # Construct URL dynamically based on the selected model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.image_model_name}:predict?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "instances": [
                {
                    "prompt": prompt
                }
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "16:9"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            # The response structure is typically:
            # {
            #   "predictions": [
            #     {
            #       "bytesBase64Encoded": "..."
            #     }
            #   ]
            # }
            
            if "predictions" in result and len(result["predictions"]) > 0:
                b64_image = result["predictions"][0]["bytesBase64Encoded"]
                image_data = base64.b64decode(b64_image)
                
                with open(output_path, "wb") as f:
                    f.write(image_data)
                    
                elapsed = time.time() - start_time
                print(f"REST API Image generation completed in {elapsed:.2f} seconds.")
                return True, f"Success ({elapsed:.2f}s)"
            else:
                error_msg = f"No image data in response: {result}"
                print(error_msg)
                self._create_placeholder_image(prompt, output_path, error_msg=error_msg)
                return False, error_msg
                
        except Exception as e:
            tb = traceback.format_exc()
            print(f"Error generating image via REST API: {e}\n{tb}")
            self._create_placeholder_image(prompt, output_path, error_msg=str(e))
            return False, str(e)

    def _create_placeholder_image(self, prompt, output_path, error_msg=None):
        try:
            img = Image.new('RGB', (1280, 720), color = (73, 109, 137))
            d = ImageDraw.Draw(img)
            
            # Try to load a font, otherwise use default
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except IOError:
                font = ImageFont.load_default()
            
            text = f"Prompt: {prompt[:100]}..."
            if error_msg:
                text += f"\n\nError: {error_msg}"
                
            d.text((50, 300), text, fill=(255, 255, 0), font=font)
            img.save(output_path)
            return True, "Placeholder Created"
        except Exception as e:
            print(f"Error creating placeholder: {e}")
            return False, str(e)
