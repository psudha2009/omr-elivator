import streamlit as st
import os
import json
import pandas as pd
from utils import preprocess_image, detect_bubbles
from omr_scoring import score_omr, load_answer_key

st.set_page_config(page_title="OMR Revaluation Dashboard", layout="wide")

st.title("📄 OMR Revaluation & Scoring System")

# Upload answer key
answer_key_file = st.file_uploader("Upload Answer Key (JSON)", type=["json"])
if answer_key_file:
    answer_key = json.load(answer_key_file)
    st.success("✅ Answer key loaded!")

# Upload OMR sheet
uploaded_image = st.file_uploader("Upload OMR Sheet", type=["jpg", "png", "jpeg"])
if uploaded_image and answer_key_file:
    with open("temp_omr.jpg", "wb") as f:
        f.write(uploaded_image.getbuffer())

    result, score = score_omr("temp_omr.jpg", answer_key)
    st.subheader(f"🧮 Score: {score}")

    df = pd.DataFrame([
        {"Question": q, "Marked": r["Marked"], "Correct": r["Correct"], "Status": r["Status"]}
        for q, r in result.items()
    ])
    st.dataframe(df)

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Result CSV", csv, "result.csv", "text/csv")

# Batch mode
st.markdown("---")
st.subheader("📦 Batch Processing")
if st.button("Run Batch on /data folder"):
    answer_key = load_answer_key("answer_keys/setA.json")
    from omr_scoring import batch_process
    batch_process("data", "answer_keys/setA.json", "results/final_scores.csv")
    st.success("Batch processing complete. Check results/final_scores.csv")
import cv2
import numpy as np

def preprocess_image(image_path):
    img = cv2.imread(image_path, 0)
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def detect_bubbles(thresh_img):
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubbles = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]
    return bubbles