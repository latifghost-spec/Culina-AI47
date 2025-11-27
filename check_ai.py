import google.generativeai as genai

# Setup the key
MY_KEY = "AIzaSyCUFP6yMMJEB8h1QvML9yqbl1frthnkSlc"
genai.configure(api_key=MY_KEY)

print("--------------------------------------")
print("🔍 CONNECTING TO GOOGLE AI...")
print("--------------------------------------")

try:
    # Ask Google for the list of available models
    found_any = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ AVAILABLE: {m.name}")
            found_any = True
    
    if not found_any:
        print("❌ No text generation models found. Check your API Key permissions.")

except Exception as e:
    print(f"❌ ERROR: {e}")

print("--------------------------------------")