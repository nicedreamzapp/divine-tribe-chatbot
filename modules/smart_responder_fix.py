# Just the fixed part for coil issues
def check_support_issue(message_lower):
    # Fix the apostrophe issue
    message_lower = message_lower.replace("'", "").replace("wont", "won't").replace("dont", "don't")
    
    if "coil" in message_lower and any(word in message_lower for word in ["wont", "not", "broken", "work"]):
        return True
    return False
