# utils/optimizer.py

def optimize_question(question: str) -> str:
    """
    Optimize the user question for better LLM understanding.
    - Trim whitespace
    - Fix common mistakes
    - Expand shorthand
    - Ensure it's framed as a clear query
    """
    question = question.strip()

    # Example optimizations (you can make this smarter later):
    replacements = {
        "prdct": "product",
        "usr": "user",
        "ordr": "order",
        "cnt": "count",
        "avg": "average",
        "amt": "amount",
    }

    for wrong, correct in replacements.items():
        question = question.replace(wrong, correct)

    # Ensure it ends with a question mark if it’s a request
    if not question.endswith("?"):
        question += "?"

    return question
