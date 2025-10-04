import google.generativeai as genai
import sys

# Check library version
print("Google GenerativeAI version:", genai.__version__)
print("Python version:", sys.version)

# Configure your API key
genai.configure(api_key="YOUR_API_KEY")

# List available models (for debugging)
try:
    models = genai.list_models()
    print("Available models:")
    for m in models:
        print("-", m.name)
except Exception as e:
    print("Could not list models:", e)

# Force free-tier model usage
try:
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    resp = model.generate_content("Hello world")
    print("✅ Response:", resp.text)
except Exception as e:
    print("❌ Error:", e)
