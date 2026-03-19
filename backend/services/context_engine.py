import datetime

class ContextEngine:
    @staticmethod
    def analyze_session(session):
        """
        Analyzes an active session and returns a smart suggestion based on rules and pings.
        """
        if not session:
            return {
                "status": "inactive", 
                "alert": "none",
                "suggestion": "You have no active session. Ready to start studying?"
            }
            
        start_time = session.get('start_time')
        current_time = datetime.datetime.utcnow()
        duration_minutes = (current_time - start_time).total_seconds() / 60.0
        
        # Phase 8: Auto-Stop Long Sessions (over 120 minutes limit logic)
        if duration_minutes > 120:
            return {
                "status": "completed",
                "alert": "auto_stop",
                "suggestion": "Session auto-stopped due to excessive length (120+ mins)."
            }

        # Rule 1: Detect Burnout (Over 60 mins)
        if duration_minutes > 60:
            return {
                "status": "warning",
                "alert": "long_session", 
                "suggestion": f"You've been studying for {int(duration_minutes)} minutes! Take a 10-minute break to avoid burnout."
            }
            
        # Phase 8: Check-in / Inactivity ping based on last_ping tracker
        last_ping = session.get('last_ping')
        minutes_since_ping = duration_minutes
        if last_ping:
            minutes_since_ping = (current_time - last_ping).total_seconds() / 60.0

        if minutes_since_ping > 30:
            return {
                "status": "active",
                "alert": "check_in",
                "suggestion": "Are you still studying? Please confirm your activity."
            }
            
        # Rule 3: Detect if there's a goal and motivate
        goal = session.get('goal')
        if goal and duration_minutes > 15:
            return {
                "status": "active", 
                "alert": "goal_check",
                "suggestion": f"You're {int(duration_minutes)} mins into your goal: '{goal}'. Keep it up!"
            }
            
        # Default active state for normal behavior
        return {
            "status": "active",
            "alert": "none",
            "suggestion": "Great start! Keep your focus."
        }
