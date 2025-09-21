import streamlit as st
import pandas as pd

# -------------------------------
# 🔑 Input Answer Key
# -------------------------------
st.title("📊 OMR Evaluation System")

st.subheader("Enter Answer Key (100 answers)")
key_input = st.text_area(
    "Paste 100 answers separated by commas (e.g. A,B,C,...)",
    height=100
)
key = [k.strip().lower() for k in key_input.split(",") if k.strip()]
valid_choices = {"a", "b", "c", "d"}

# -------------------------------
# 📚 Section Mapping
# -------------------------------
st.subheader("Define Sections")
section_input = st.text_area(
    "Define sections (e.g. Python:0-20, EDA:20-40, MySQL:40-60, Power BI:60-80, Adv Stats:80-100)",
    value="Python:0-20, EDA:20-40, MySQL:40-60, Power BI:60-80, Adv Stats:80-100"
)

sections = {}
try:
    for part in section_input.split(","):
        name, rng = part.split(":")
        start, end = map(int, rng.split("-"))
        sections[name.strip()] = (start, end)
except:
    st.error("❌ Invalid section format. Use Section:Start-End")

# -------------------------------
# 🧾 Enter Candidate Responses
# -------------------------------
st.subheader("Enter Candidate Answers")
num_candidates = st.number_input(
    "Number of Candidates",
    min_value=1,
    max_value=50,
    value=1
)

candidates = []
for i in range(num_candidates):
    st.markdown(f"**Candidate {i+1}**")
    set_name = st.selectbox(
        f"Set for Candidate {i+1}",
        ["A", "B"],
        key=f"set_{i}"
    )
    answers_input = st.text_area(
        f"Answers for Candidate {i+1} (comma-separated)",
        key=f"ans_{i}"
    )
    answers = [a.strip().lower() for a in answers_input.split(",") if a.strip()]
    candidates.append({"set": set_name, "answers": answers})

# -------------------------------
# 🧮 Scoring Logic
# -------------------------------
def score_candidate(candidate, index):
    result = {"Candidate": f"Candidate {index+1}", "Set": candidate["set"]}
    total = 0
    for section, (start, end) in sections.items():
        score = sum([
            a == k
            for a, k in zip(candidate["answers"][start:end], key[start:end])
        ])
        result[section] = score
        result[section + " (%)"] = round((score / (end - start)) * 100, 2)
        total += score
    result["Total"] = total
    result["Total (%)"] = round((total / 100) * 100, 2)
    return result

# -------------------------------
# ✅ Validation
# -------------------------------
def validate_all():
    if len(key) != 100:
        st.warning("⚠️ Answer key must contain exactly 100 answers.")
        return False
    if not all(k in valid_choices for k in key):
        st.warning("⚠️ Answer key contains invalid choices. Only A, B, C, D are allowed.")
        return False
    for i, c in enumerate(candidates):
        if len(c["answers"]) != 100:
            st.warning(f"⚠️ Candidate {i+1} must have exactly 100 answers.")
            return False
        if not all(a in valid_choices for a in c["answers"]):
            st.warning(f"⚠️ Candidate {i+1} has invalid answers. Only A, B, C, D are allowed.")
            return False
    return True

# -------------------------------
# 📊 Display Results
# -------------------------------
if validate_all():
    results = [score_candidate(c, i) for i, c in enumerate(candidates)]
    df = pd.DataFrame(results)
    st.subheader("✅ Evaluation Results")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        label="📥 Download Results as CSV",
        data=df.to_csv(index=False),
        file_name="omr_results.csv",
        mime="text/csv"
    )