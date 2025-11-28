import google.generativeai as genai
import sys

try:
    api_key = sys.argv[1]
    genai.configure(api_key=api_key)

    print("Listing models...")
    found_imagen = False
    for m in genai.list_models():
        print(f"Name: {m.name}")
        print(f"Supported methods: {m.supported_generation_methods}")
        if 'imagen' in m.name.lower() or 'image' in m.supported_generation_methods:
            found_imagen = True
        print("-" * 20)
    
    if not found_imagen:
        print("No explicit image generation models found in list_models().")

except Exception as e:
    print(f"Error: {e}")
