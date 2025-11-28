import google.generativeai as genai
import os

print(f"SDK Version: {genai.__version__}")

print("\n--- Module Attributes ---")
print(dir(genai))

if 'ImageGenerationModel' in dir(genai):
    print("\nSUCCESS: ImageGenerationModel found in genai module.")
else:
    print("\nFAILURE: ImageGenerationModel NOT found in genai module.")

