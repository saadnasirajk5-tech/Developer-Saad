import re 
def check_password_strength(password):
    score = 0 
    feedback = [] 
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1 
    else:
        feedback.append("pass too short") 
        
    if re.search(r"[A-Z]",password):
        score += 1 
    else:
        feedback.append("Add uppercase letters") 
    if re.search(r"[a-z]",password):
        score += 1 
    else:
        feedback.append("Add lowercase letters")
    
        # Numbers
    if re.search(r"[0-9]", password):
        score += 1
    else:
        feedback.append("Add numbers")

    # Special characters
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 2
    else:
        feedback.append("Add special characters")
        
        # Common weak patterns
    weak_patterns = ["12345", "password", "qwerty", "abc123"]
    for pattern in weak_patterns:
        if pattern in password.lower():
            score -= 2
            feedback.append("Avoid common patterns")
            break

    return score, feedback


def get_strength_label(score):
    if score <= 2:
        return "Weak"
    elif score <= 5:
        return "Medium"
    else:
        return "Strong"


# Main program
password = input("Enter your password: ")

score, feedback = check_password_strength(password)
strength = get_strength_label(score)

print(f"\nStrength: {strength}")
print(f"Score: {score}")

if feedback:
    print("Suggestions:")
    for f in feedback:
        print("-", f)

























