.

🧠 What Is This Project?
This is a fully automated OMR (Optical Mark Recognition) evaluation system built with Python, OpenCV, and Streamlit. It’s designed to help educators and evaluators accurately score multiple-choice answer sheets with minimal manual effort — while maintaining full transparency, auditability, and fairness.

🎯 What Problem Does It Solve?
Manual evaluation of OMR sheets is time-consuming, error-prone, and difficult to audit. This system solves that by:
- Automatically detecting marked bubbles using image processing
- Parsing dynamic answer keys from Excel files
- Scoring responses with both strict and lenient logic
- Handling multi-marked bubbles, unanswered questions, and ambiguous cases
- Providing subject-wise analytics and diagnostic feedback

🛠️ How Does It Work?
- Upload the scanned OMR sheet (JPG/PNG)
- Upload the answer key Excel file (supports multiple sets like Set A, Set B)
- The system:
- Detects bubbles using OpenCV
- Measures bubble darkness to determine marked answers
- Parses the answer key using regex
- Maps detected answers to questions
- Scores each response with clear logic
- Breaks down scores by subject (Python, SQL, EDA, etc.)
- Streamlit dashboard displays:
- Uploaded sheet preview
- Parsed answer key
- Detected answers
- Scoring breakdown
- Accuracy percentage
- Subject-wise scores
- Warnings for overmarked or missing answers

🔍 Why Is It Special?
- Evaluator-friendly: Designed for real-world use with clear diagnostics
- Audit-ready: Transparent scoring logic and warnings for ambiguous cases
- Modular and scalable: Easy to extend, customize, and deploy
- Streamlit-powered: Runs in the browser, no installation needed

🌐 Live Demo
Once deployed on Streamlit Cloud, users can access it at:
https://psudha2009-omr-elivator.streamlit.app


Just upload your sheet and key — the system does the rest.

