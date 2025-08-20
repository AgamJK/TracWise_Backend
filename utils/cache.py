from config import db
import hashlib
from datetime import datetime, timedelta

def normalize_question(question):
    """Normalize question for consistent matching"""
    return question.lower().strip().replace("?", "").replace(".", "")

def get_question_hash(question):
    """Create a hash for the question for efficient lookup"""
    normalized = normalize_question(question)
    return hashlib.md5(normalized.encode()).hexdigest()

def get_cached_answer(question):
    """Get cached answer if available and not expired"""
    try:
        question_hash = get_question_hash(question)
        
        # Look for exact match first
        cache_entry = db.qa_cache.find_one({
            "question_hash": question_hash,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if cache_entry:
            print(f"Cache HIT for question: {question[:50]}...")
            # Update hit count and last accessed
            db.qa_cache.update_one(
                {"_id": cache_entry["_id"]},
                {
                    "$inc": {"hit_count": 1},
                    "$set": {"last_accessed": datetime.utcnow()}
                }
            )
            return cache_entry.get("answer")
        
        # Try fuzzy matching for similar questions
        similar_entry = find_similar_cached_question(question)
        if similar_entry:
            print(f"Cache SIMILAR HIT for question: {question[:50]}...")
            return similar_entry.get("answer")
            
        print(f"Cache MISS for question: {question[:50]}...")
        return None
        
    except Exception as e:
        print(f"Error retrieving from cache: {str(e)}")
        return None

def cache_answer(question, answer, model="General", ttl_hours=24):
    """Cache the question-answer pair"""
    try:
        question_hash = get_question_hash(question)
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        cache_entry = {
            "question": question,
            "question_hash": question_hash,
            "normalized_question": normalize_question(question),
            "answer": answer,
            "model": model,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "hit_count": 0,
            "last_accessed": datetime.utcnow()
        }
        
        # Upsert (update if exists, insert if not)
        db.qa_cache.update_one(
            {"question_hash": question_hash},
            {"$set": cache_entry},
            upsert=True
        )
        
        print(f"Cached answer for question: {question[:50]}...")
        return True
        
    except Exception as e:
        print(f"Error caching answer: {str(e)}")
        return False

def find_similar_cached_question(question, similarity_threshold=0.8):
    """Find similar questions using simple text matching"""
    try:
        normalized_question = normalize_question(question)
        words = set(normalized_question.split())
        
        if len(words) < 3:  # Too short for meaningful similarity
            return None
        
        # Find cached questions with overlapping words
        pipeline = [
            {"$match": {"expires_at": {"$gt": datetime.utcnow()}}},
            {"$limit": 50}  # Limit for performance
        ]
        
        cached_questions = list(db.qa_cache.aggregate(pipeline))
        
        for cached in cached_questions:
            cached_words = set(cached.get("normalized_question", "").split())
            if len(cached_words) < 3:
                continue
                
            # Calculate simple word overlap similarity
            intersection = words.intersection(cached_words)
            union = words.union(cached_words)
            
            if len(union) > 0:
                similarity = len(intersection) / len(union)
                if similarity >= similarity_threshold:
                    print(f"Found similar question with {similarity:.2f} similarity")
                    return cached
        
        return None
        
    except Exception as e:
        print(f"Error finding similar questions: {str(e)}")
        return None

def get_cache_stats():
    """Get cache statistics"""
    try:
        total_cached = db.qa_cache.count_documents({})
        active_cached = db.qa_cache.count_documents({"expires_at": {"$gt": datetime.utcnow()}})
        
        # Get most popular questions
        popular_questions = list(db.qa_cache.find(
            {"expires_at": {"$gt": datetime.utcnow()}},
            {"question": 1, "hit_count": 1, "_id": 0}
        ).sort("hit_count", -1).limit(5))
        
        return {
            "total_cached_questions": total_cached,
            "active_cached_questions": active_cached,
            "popular_questions": popular_questions
        }
        
    except Exception as e:
        print(f"Error getting cache stats: {str(e)}")
        return {}

def clear_expired_cache():
    """Remove expired cache entries"""
    try:
        result = db.qa_cache.delete_many({"expires_at": {"$lt": datetime.utcnow()}})
        print(f"Cleared {result.deleted_count} expired cache entries")
        return result.deleted_count
        
    except Exception as e:
        print(f"Error clearing expired cache: {str(e)}")
        return 0
