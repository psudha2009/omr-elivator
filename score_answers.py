# score_answers.py

def score_answers(predicted_answers, answer_key):
    """
    Scores predicted answers against the answer key.
    - Single-answer questions require exact match.
    - Multi-answer questions accept any correct option.
    Returns detailed scoring breakdown and accuracy.
    """
    min_len = min(len(predicted_answers), len(answer_key))
    predicted_trimmed = predicted_answers[:min_len]
    key_trimmed = answer_key[:min_len]

    scoring_details = []
    correct = 0

    for i, (pred, actual) in enumerate(zip(predicted_trimmed, key_trimmed), start=1):
        actual_options = [opt.strip() for opt in actual.split(",") if opt.strip()]
        is_multi = len(actual_options) > 1

        if is_multi:
            is_correct = pred in actual_options
            mode = "Lenient"
        else:
            is_correct = pred == actual_options[0]
            mode = "Strict"

        scoring_details.append({
            "Q.No": i,
            "Predicted": pred,
            "Actual": actual,
            "Correct": "✅" if is_correct else "❌",
            "Mode": mode
        })

        if is_correct:
            correct += 1

    accuracy = correct / min_len if min_len > 0 else 0
    return scoring_details, correct, min_len, accuracy