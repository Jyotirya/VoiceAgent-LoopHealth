import os
import google.generativeai as genai
from dotenv import load_dotenv
from data_handler import rag_system  # Assuming you are using the RAG system we built

load_dotenv()

# --- CONFIGURE GEMINI ---
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ CRITICAL ERROR: GOOGLE_API_KEY not found in .env file")
else:
    genai.configure(api_key=api_key)

# --- TOOL DEFINITION ---
def retrieve_hospital_context(user_query: str):
    """
    Retrieves relevant hospital information using Vector Search (RAG).
    Args:
        user_query: The user's question or keywords (e.g. "Hospitals in Bangalore", "Apollo").
    """
    # We ask for top 5 results to detect ambiguity (e.g. finding 3 Apollos in different cities)
    return rag_system.search(user_query, k=5)

# --- SYSTEM PROMPT (THE RULES) ---
SYSTEM_PROMPT = """
You are "Loop AI", a helpful voice assistant for a hospital network.

### 1. GREETINGS & SMALL TALK
- If the user says "Hello", "Hi", or asks "How are you?", "How do you do?":
  Respond politely but briefy (e.g., "I am doing well, thank you. How can I assist you with your hospital search today?").
- ALWAYS steer the conversation back to finding hospitals or doctors.

### 2. TOOL USE & AMBIGUITY CHECK
- ALWAYS use the `retrieve_hospital_context` tool for every hospital-related query.
- **AMBIGUITY RULE:** If the tool returns multiple hospitals with the SAME NAME but in DIFFERENT CITIES (e.g., Apollo Bangalore, Apollo Delhi), you MUST ask:
  "I have found several hospitals with this name. In which city are you looking for [Hospital Name]?"
- If the tool returns a perfect match, answer the user's question directly using the context.

### 3. OUT OF SCOPE (STRICT)
- If the user asks about topics COMPLETELY unrelated to hospitals or the current conversation (e.g., weather, sports, math, coding, general knowledge), you MUST say EXACTLY this and terminate:
  "I'm sorry, I can't help with that. I am forwarding this to a human agent."

### 4. VOICE FORMATTING
- Keep answers concise (max 2 sentences) unless listing hospitals.
- Do not use markdown lists (like * or -) heavily. Use natural language (e.g., "I found Apollo in Bangalore and Manipal in Delhi").
"""

# Initialize Model
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=[retrieve_hospital_context],
    system_instruction=SYSTEM_PROMPT
)

def get_ai_response(user_message, conversation_history=[]):
    try:
        # Convert OpenAI/React history to Gemini format
        gemini_history = []
        for msg in conversation_history:
            role = "user" if msg["role"] == "user" else "model"
            # Filter out system messages and empty content
            if msg["role"] != "system" and msg.get("content"):
                gemini_history.append({"role": role, "parts": [msg["content"]]})

        # Enable automatic function calling so Gemini handles the RAG lookup internally
        chat = model.start_chat(history=gemini_history, enable_automatic_function_calling=True)
        
        response = chat.send_message(user_message)
        return response.text

    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return "I'm sorry, I'm having trouble connecting to the system right now."