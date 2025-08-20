from flask import Blueprint, request, jsonify
from utils.gemini import ask_gemini
from models.manual import find_manual
from utils.cache import get_cached_answer, cache_answer, get_cache_stats, clear_expired_cache
import time

qa_bp = Blueprint("qa", __name__)

@qa_bp.route("/", methods=["POST"])
def ask():
    start_time = time.time()
    
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        question = data.get("question", "").strip()
        model = data.get("model", "General")
        conversation_history = data.get("conversation_history", [])
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        # 🚀 STEP 1: Check cache first (only for simple questions without conversation context)
        cached_answer = None
        if not conversation_history:  # Only use cache if no conversation history
            cached_answer = get_cached_answer(question)
        
        if cached_answer:
            response_time = round((time.time() - start_time) * 1000, 2)
            return jsonify({
                "answer": cached_answer,
                "model_used": model,
                "cached": True,
                "response_time_ms": response_time,
                "source": "cache"
            })
        
        # 🔍 STEP 2: Cache miss - get from manual + AI
        print("Cache miss - querying AI...")
        
        # Find relevant manual section
        manual = find_manual({"model": model})
        
        if manual and manual.get("content"):
            context = manual.get("content", "")
            print(f"Found manual for model: {model}, content length: {len(context)}")
        else:
            # If no specific model manual found, try to find any available manual
            manual = find_manual({})
            context = manual.get("content", "") if manual else ""
            print(f"Using general manual content, length: {len(context)}")
            if not context:
                print("WARNING: No manual content found in database!")
        
        print(f"Context preview: {context[:200]}..." if context else "No context available")
        
        # Get AI response with conversation history
        answer = ask_gemini(question, context, conversation_history)
        
        # 💾 STEP 3: Cache the answer for future use (only for simple questions without conversation context)
        if answer and "Sorry, I couldn't" not in answer and not conversation_history:
            cache_answer(question, answer, model, ttl_hours=168)  # Cache for 1 week
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            "answer": answer,
            "model_used": model,
            "manual_found": bool(context),
            "context_length": len(context),
            "cached": False,
            "response_time_ms": response_time,
            "source": "ai_generated"
        })
        
    except Exception as e:
        print(f"Error in QA route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@qa_bp.route("/cache/stats", methods=["GET"])
def cache_statistics():
    """Get cache performance statistics"""
    try:
        stats = get_cache_stats()
        return jsonify(stats)
    except Exception as e:
        print(f"Error getting cache stats: {str(e)}")
        return jsonify({"error": "Could not retrieve cache statistics"}), 500

@qa_bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """Clear expired cache entries"""
    try:
        cleared_count = clear_expired_cache()
        return jsonify({
            "message": f"Successfully cleared {cleared_count} expired cache entries",
            "cleared_count": cleared_count
        })
    except Exception as e:
        print(f"Error clearing cache: {str(e)}")
        return jsonify({"error": "Could not clear cache"}), 500