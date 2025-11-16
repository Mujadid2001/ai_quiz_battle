import random
from makequestions import get_api_questions

# ================================
# AI Taunts
# ================================
ai_taunts = [
    "Hehe 😈 I knew you’d miss that.",
    "Nice try human!",
    "You think you can beat me?",
    "AI supremacy activated 😎",
]

# ================================
# Prepare final question set
# ================================
questions = []

# Add API questions
questions.extend(get_api_questions(5))

# Shuffle all questions
random.shuffle(questions)

# ================================
# The Game Loop
# ================================
score = 0

print("=== AI QUIZ BATTLE ===")
print("Beat the AI if you can...\n")

for q in questions:
    print(q["q"])

    # If question has options, show them
    if q["options"]:
        for idx, opt in enumerate(q["options"], 1):
            print(f"{idx}. {opt}")

        user_raw = input("Your answer (type answer or number): ").strip().lower()

        # Allow user to choose by index or text
        if user_raw.isdigit():
            index = int(user_raw) - 1
            if 0 <= index < len(q["options"]):
                user_answer = q["options"][index].lower()
            else:
                user_answer = ""
        else:
            user_answer = user_raw

    else:
        # Custom question (no options)
        user_answer = input("Your answer: ").strip().lower()

    # Check answer
    if user_answer == q["correct"]:
        score += 1
        print("Correct! 🎉")
    else:
        print("Wrong!", random.choice(ai_taunts))
        print(f"The correct answer was: {q['correct']}")

    print("-" * 40)

# ================================
# Final Score
# ================================
print(f"Your final score: {score}/{len(questions)} 🏆")
print("Thanks for playing AI Quiz Battle!")
