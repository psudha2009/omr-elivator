import streamlit as st
import pandas as pd
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from bubble_detector import detect_bubbles
import re

st.set_page_config(page_title="OMR Evaluation System", layout="wide")
st.title("📝 Automated OMR Evaluation System")

uploaded_sheet = st.file_uploader("Upload scanned OMR sheet", type=["jpg", "png", "jpeg"])
uploaded_key = st.file_uploader("Upload Answer Key Excel (Set A and Set B)", type=["xlsx"])

if uploaded_sheet and uploaded_key:
    st.image(uploaded_sheet, caption="Uploaded Sheet", use_container_width=True)
    image = Image.open(BytesIO(uploaded_sheet.getbuffer()))

    try:
        df_key = pd.read_excel(uploaded_key)
        df_key.columns = df_key.columns.str.strip()
        available_columns = df_key.columns.tolist()
        st.write("📄 Available columns in Excel:", available_columns)

        selected_column = st.selectbox("Choose the correct set:", available_columns)
        selected_column = selected_column.strip()

        def parse_key(df, selected_column):
            key_map = {}
            for row in df[selected_column].dropna():
                text = str(row).strip().lower()
                match = re.match(r"(\d+)[\s\.\-\:]*([a-e](?:,[a-e])*)", text)
                if match:
                    qnum = int(match.group(1))
                    raw_ans = match.group(2)
                    valid = [opt for opt in raw_ans.split(",") if opt in {"a", "b", "c", "d", "e"}]
                    if valid:
                        key_map[qnum] = ",".join(valid)
            return key_map

        key_map = parse_key(df_key, selected_column)
        st.write(f"✅ Parsed {len(key_map)} answers from the key")
    except Exception as e:
        st.error(f"❌ Failed to read Excel file: {e}")
        key_map = {}

    if key_map:
        bubble_data, gray_image = detect_bubbles(image)
        st.write(f"🔍 Total bubbles detected: {len(bubble_data)}")

        def map_bubbles_to_answers(bubble_data, gray_image, threshold=120):
            sorted_bubbles = sorted(bubble_data, key=lambda b: (b["center"][1], b["center"][0]))
            predicted_answers = []

            for i in range(0, len(sorted_bubbles), 5):
                group = sorted_bubbles[i:i+5]
                if len(group) < 5:
                    continue

                marked = []
                for idx, bubble in enumerate(group):
                    mask = np.zeros(gray_image.shape, dtype=np.uint8)
                    cv2.drawContours(mask, [bubble["contour"]], -1, 255, -1)
                    mean_val = cv2.mean(gray_image, mask=mask)[0]
                    if mean_val < threshold:
                        marked.append(["a", "b", "c", "d", "e"][idx])

                predicted_answers.append(",".join(marked) if marked else "")

            return predicted_answers

        predicted_answers = map_bubbles_to_answers(bubble_data, gray_image)
        predicted_map = {i + 1: ans for i, ans in enumerate(predicted_answers)}
        st.write("🧠 Mapped Answers:", predicted_map)
        st.write(f"✅ Questions scored: {len(predicted_answers)}")

        scoring_details = []
        correct = 0
        overmarked_count = 0

        for qnum in key_map:
            pred = predicted_map.get(qnum, "")
            actual = key_map.get(qnum, "")

            pred_set = set(pred.split(",")) if pred else set()
            actual_set = set(actual.split(",")) if actual else set()

            if not actual_set:
                is_correct = False
                mode = "No Key"
                scoring = "No answer key available"
            elif not pred_set:
                is_correct = False
                mode = "Unanswered"
                scoring = "No bubble marked"
            elif len(actual_set) == 1:
                if len(pred_set) == 1 and pred_set == actual_set:
                    is_correct = True
                    mode = "Strict"
                    scoring = "Exact match"
                else:
                    is_correct = False
                    mode = "Overmarked"
                    scoring = "Multiple bubbles marked for single-answer question"
                    overmarked_count += 1
            else:
                is_correct = bool(pred_set & actual_set)
                mode = "Lenient"
                scoring = "Any correct bubble accepted"

            scoring_details.append({
                "Q.No": qnum,
                "Predicted": pred,
                "Actual": actual,
                "Correct": "✅" if is_correct else "❌",
                "Mode": mode,
                "Scoring": scoring
            })

            if is_correct:
                correct += 1

        accuracy = correct / len(key_map) if key_map else 0

        st.subheader("📊 Detailed Scoring Results")
        st.dataframe(pd.DataFrame(scoring_details))

        st.subheader("✅ Overall Accuracy")
        st.write(f"**{correct} out of {len(key_map)}** correct")
        st.write(f"Accuracy: **{accuracy:.2%}**")

        if overmarked_count > 0:
            st.warning(f"⚠️ {overmarked_count} questions were marked with multiple bubbles but expected only one. These were treated as incorrect.")

        st.subheader("📈 Subject-wise Scores")

        subjects = ["Python", "EDA", "SQL", "POWER BI", "Statistics"]
        questions_per_subject = 20
        subject_scores = {}
        missing_subjects = []

        for i, subject in enumerate(subjects):
            start_q = i * questions_per_subject + 1
            end_q = start_q + questions_per_subject
            sub_correct = 0
            has_key = False

            for qnum in range(start_q, end_q):
                if qnum not in key_map or qnum not in predicted_map:
                    continue
                has_key = True
                pred = predicted_map[qnum]
                actual = key_map[qnum]
                p_set = set(pred.split(",")) if pred else set()
                a_set = set(actual.split(",")) if actual else set()
                if not a_set:
                    continue
                elif len(a_set) == 1:
                    if len(p_set) == 1 and p_set == a_set:
                        sub_correct += 1
                else:
                    if p_set & a_set:
                        sub_correct += 1

            if has_key:
                subject_scores[subject] = sub_correct
            else:
                missing_subjects.append(subject)

        if subject_scores:
            score_table = pd.DataFrame({
                "Subject": list(subject_scores.keys()),
                f"Score (out of {questions_per_subject})": list(subject_scores.values())
            })

            total_score = sum(subject_scores.values())
            total_possible = questions_per_subject * len(subject_scores)
            total_row = pd.DataFrame({
                "Subject": ["Total"],
                f"Score (out of {questions_per_subject})": [f"{total_score} out of {total_possible}"]
            })

            score_table = pd.concat([score_table, total_row], ignore_index=True)
            st.dataframe(score_table)

        if missing_subjects:
            st.warning(f"⚠️ No answer key found for: {', '.join(missing_subjects)}")