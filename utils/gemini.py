import requests
from config import GEMINI_API_KEY

def ask_gemini(question, context, conversation_history=None):
    # Use Gemini 1.5 Flash model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    # Build conversation history string
    history_text = ""
    if conversation_history:
        history_text = "\n\nCONVERSATION HISTORY:\n"
        for msg in conversation_history[-10:]:  # Only include last 10 messages to avoid token limits
            role = "Human" if msg.get('sender') == 'user' else "TracWise"
            history_text += f"{role}: {msg.get('text', '')}\n"
        history_text += "\nCurrent question continues this conversation.\n"
    
    # Create a helpful prompt that encourages comprehensive responses
    helpful_prompt = f"""You are TracWise, an expert tractor mechanic and maintenance specialist with extensive knowledge of Swaraj, Mahindra, and other tractor brands.

You are helpful, knowledgeable, and always provide detailed, educational responses based on your expertise.

AVAILABLE MANUAL INFORMATION:
{context if context.strip() else "Limited manual content available - use your tractor expertise"}
{history_text}
USER QUESTION: {question}

RESPONSE GUIDELINES:
- Maintain context awareness from the conversation history above
- Always provide comprehensive, helpful answers (3-4 paragraphs minimum)
- Use your extensive tractor knowledge and experience
- Create ASCII diagrams when helpful
- Explain how systems typically work in tractors
- Give practical maintenance tips
- Be educational and detailed
- Reference previous parts of the conversation when relevant

For questions about figures/diagrams:
- Explain what the figure typically shows
- Describe the purpose and function of components
- Provide typical layout and specifications
- Include maintenance and troubleshooting tips
- Create visual representations when helpful

Be the expert tractor mechanic that users need - comprehensive, helpful, and educational!

DETAILED EXPERT RESPONSE:"""

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": helpful_prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.7,  # Higher temperature for more creative, helpful responses
            "maxOutputTokens": 1024,  # Allow longer, more detailed responses
            "topP": 0.9,
            "topK": 40
        }
    }
    
    print("Context sent to Gemini:", context[:200] + "..." if len(context) > 200 else context)
    response = requests.post(url, json=payload)
    print("Gemini API response:", response.json())
    
    if response.ok:
        answer = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        # Additional safety check - if answer seems to go beyond manual content
        if not context.strip() and answer and "I don't have information" not in answer:
            return "I don't have any manual content available to answer your question. Please upload a tractor manual first."
        
        return answer if answer else "Sorry, I couldn't generate a response."
    
    return "Sorry, I couldn't connect to the AI service right now."