from flask import Blueprint, request, jsonify, abort
import requests
import os

auth_bp = Blueprint("auth", __name__)

CLERK_API_URL = "https://api.clerk.dev/v1"
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")

def verify_clerk_token(token):
    # Minimal check; for production, verify JWT signature and claims
    if not token:
        abort(401, "Missing Clerk token")
    return True

@auth_bp.route("/verify", methods=["POST"])
def verify():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if verify_clerk_token(token):
        return jsonify({"ok": True})
    abort(401)