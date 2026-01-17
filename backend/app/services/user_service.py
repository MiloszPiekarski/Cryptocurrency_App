import firebase_admin
from firebase_admin import credentials, firestore, auth
from app.services.email_service import EmailService
from loguru import logger
import asyncio
import json
import os
from datetime import datetime

# Path: backend/data/users.json
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "users.json")
if not os.path.exists(os.path.dirname(DATA_FILE)):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Helper: Load Users
def _load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load users.json: {e}")
        return {}

# Helper: Save Users
def _save_users(users):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save users.json: {e}")

# Lazy init of Firebase Admin
def get_firestore_db():
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.success("🔥 Firebase Admin Initialized")
        except Exception as e:
            logger.error(f"Failed to init Firebase Admin: {e}")
            raise e
    return firestore.client()

class UserService:
    
    @staticmethod
    def init_table():
        """Ensure connection to DB models exists - NOOP for JSON persistence"""
        pass

    @staticmethod
    def sync_user(firebase_uid: str, email: str = None):
        """Sync Firebase Auth user to JSON persistence layer"""
        try:
            users = _load_users()

            if firebase_uid in users:
                # User exists
                current_plan = users[firebase_uid].get("plan", "FREE")
                
                # Update email if missing/changed (optional housekeeping)
                if email and users[firebase_uid].get("email") != email:
                    users[firebase_uid]["email"] = email
                    _save_users(users)
                    
                return {"status": "exists", "plan": current_plan}

            # 2. Register New User
            logger.info(f"Registering new user: {firebase_uid} ({email})")

            users[firebase_uid] = {
                "email": email,
                "plan": "FREE",
                "created_at": datetime.now().isoformat()
            }
            _save_users(users)

            # 3. Send CUSTOM Verification Email (replacing Google's default)
            if email:
                try:
                    # Ensure Firebase Admin is initialized before using auth
                    get_firestore_db()
                    
                    # Generate the link via Admin SDK
                    # This link, when clicked, verifies the user in Firebase Auth.
                    verification_link = auth.generate_email_verification_link(email)
                    logger.info(f"Generated verification link for {email}")

                    EmailService.send_new_user_welcome(email, verification_link)
                except Exception as email_err:
                    logger.error(f"Failed to send welcome/verification email: {email_err}")
                    # Don't fail sync, but log heavily because user cannot verify otherwise

            return {"status": "created", "plan": "FREE"}
            
        except Exception as e:
            logger.error(f"Sync User Failed: {e}")
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def simulate_payment(firebase_uid: str):
        """Simulate payment, upgrade plan, and email user"""
        print(f"DEBUG: Starting simulate_payment for {firebase_uid}")
        
        # Ensure Firebase Admin is initialized (needed for auth maybe?)
        try:
            get_firestore_db()
        except Exception as e:
            logger.warning(f"Firebase init check failed: {e}")

        # 1. Processing Delay
        await asyncio.sleep(2)
        
        new_plan = "PRO"
        
        try:
            users = _load_users()
            
            user_data = users.get(firebase_uid)
            if not user_data:
                # Edge case: User needs to be created on the fly
                logger.warning(f"Upgrading unknown user {firebase_uid}")
                try:
                    fb_user = auth.get_user(firebase_uid)
                    user_email = fb_user.email
                except:
                    user_email = None
                
                user_data = {
                    "email": user_email,
                    "plan": "FREE", # Will update below
                    "created_at": datetime.now().isoformat()
                }
                users[firebase_uid] = user_data
            
            # 2. Update Plan in JSON
            users[firebase_uid]["plan"] = new_plan
            _save_users(users)
            
            # 3. Send Premium Welcome Email
            user_email = users[firebase_uid].get("email")
            if user_email:
                print(f"DEBUG: Attempting to send premium email to {user_email}")
                EmailService.send_premium_welcome(user_email)
            else:
                logger.warning(f"No email found for user {firebase_uid}, skipping premium email.")

            return {"success": True, "new_plan": new_plan}
            
        except Exception as e:
            logger.error(f"Payment Simulation Failed: {e}")
            return {"success": False, "error": str(e)}

    # New Feature: Watchlist (JSON Stub for compatibility)
    @staticmethod
    def add_to_watchlist(firebase_uid: str, symbol: str):
        # For now, just log it or save to JSON if needed. 
        # The user was complaining about LOGIN/EMAILS, not watchlist.
        # Let's add simple JSON support for watchlist to be safe.
        try:
            users = _load_users()
            if firebase_uid in users:
                watchlist = users[firebase_uid].get("watchlist", [])
                if symbol not in watchlist:
                    watchlist.append(symbol)
                    users[firebase_uid]["watchlist"] = watchlist
                    _save_users(users)
            return {"status": "added", "symbol": symbol}
        except Exception as e:
            logger.error(f"Add Watchlist Failed: {e}")
            return {"error": str(e)}
