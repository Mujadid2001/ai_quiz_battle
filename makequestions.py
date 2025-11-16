import html
import random
from api_client import cached_get
# ================================
# Fetch Questions from API
# ================================
def get_api_questions(n=5, cache_ttl=60*60*24*7):
    url = "https://opentdb.com/api.php"
    params = {"amount": n, "type": "multiple"}
    res = cached_get(url, params=params, ttl=cache_ttl)

    questions = []

    for item in res["results"]:
        question = html.unescape(item["question"])
        correct = html.unescape(item["correct_answer"])
        wrong = [html.unescape(x) for x in item["incorrect_answers"]]

        # Shuffle options
        options = wrong + [correct]
        random.shuffle(options)

        questions.append({
            "q": question,
            "correct": correct.lower(),
            "options": options
        })
    # Your Custom Questions
    # ================================
    custom_questions = [
        {"q": "What is the capital of France?", "correct": "paris"},
        {"q": "2 + 2 * 2 = ?", "correct": "6"},
        {"q": "Who created Python?", "correct": "guido van rossum"},
    ]
    # Add custom questions (convert to uniform format)
    for cq in custom_questions:
        questions.append({
            "q": cq["q"],
            "correct": cq["correct"],
            "options": None
        })


    return questions
