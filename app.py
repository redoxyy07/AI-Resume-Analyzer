import streamlit as st
from docx import Document
import google.generativeai as genai
import os


api_key = os.environ.get("GENAI_API_KEY")  # Reads system variable
genai.configure(api_key=api_key)

# ---------------- Header ----------------
st.header("🤖 AI Job Recruiter – Resume Screening")

# ---------------- Load Skills ----------------
try:
    with open("Skills.txt", "r") as file:
        total_skills = [i.strip().lower() for i in file]
except:
    st.error("⚠️ Skills file is missing")
    total_skills = []

# ---------------- Load Job Descriptions ----------------
try:
    with open("Job Description.txt", "r") as file:
        skills_dict = {}
        for line in file:
            if ":" in line:
                domain, skill = line.split(":", 1)
                skills = [s.strip().lower() for s in skill.split(",")]
                skills_dict[domain.strip()] = skills
except:
    st.error("⚠️ Job Description file is missing")
    skills_dict = {}

# ---------------- Tabs ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Input File", "Job Domain", "Skills Matching", "ATS Score", "Improvement Suggestions"]
)

# ---------------- Tab 1: Upload Resume ----------------
with tab1:
    st.subheader("Upload Resume")
    u_file = st.file_uploader("Upload your Resume (.docx): ")

    if u_file:
        try:
            doc = Document(u_file)
            text = "\n".join([p.text for p in doc.paragraphs])

            with st.expander("📄 Resume Preview"):
                st.text(text[:400])

            resume_skills = [i for i in total_skills if i in text.lower()]
            st.subheader("🧠 Skills Found:")
            st.write(", ".join(resume_skills) if resume_skills else "No matching skills found")

        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("Please upload your resume")

# ---------------- Tab 2: Job Domain ----------------
with tab2:
    st.subheader("Job Domain Matching")
    if u_file:
        if skills_dict:
            jd = st.selectbox("Select Job Domain", list(skills_dict.keys()))
            required = skills_dict[jd]
            st.write("Required Skills:", ", ".join(required))
    else:
        st.warning("Upload resume first")

# ---------------- Tab 3: Skills Match ----------------
with tab3:
    st.subheader("Skills Match Result")
    if u_file and skills_dict:
        match = [i for i in required if i in resume_skills]
        miss = [i for i in required if i not in resume_skills]

        st.success(f"Matched: {', '.join(match) if match else 'None'}")
        st.error(f"Missing: {', '.join(miss) if miss else 'None'}")
    else:
        st.warning("Complete previous steps first")

# ---------------- Tab 4: ATS Score ----------------
with tab4:
    st.subheader("ATS Score")
    if u_file and skills_dict:
        if len(required) > 0:
            ats = round((len(match) / len(required)) * 100, 2)
            st.write(f"ATS Score: **{ats}%**")

            if ats >= 70:
                st.success("Strong Resume")
            elif ats >= 50:
                st.warning("Moderate Resume – improve further")
            else:
                st.error("Weak Resume")
    else:
        st.warning("Complete previous steps first")

# ---------------- Tab 5: Improvement Suggestions ----------------
with tab5:
    st.subheader("Improvement Suggestions (AI)")

    if u_file:
        if 'miss' in locals() and miss:
            for skill in miss:
                st.write(f"### 🔹 {skill.upper()}")

                prompt = f"""
                Skill: {skill}
                Generate improvement suggestions:
                1. Skill Level Needed (Basic/Intermediate/Pro)
                2. Why it is important (2 short lines)
                3. One mini-project idea (only topic)
                4. Three free learning links (real URLs)
                Keep it short and clean.
                """

                try:
                    model = genai.GenerativeModel("models/gemini-2.5-flash")
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error for {skill}: {e}")
        else:
            st.success("🎉 No missing skills!")
    else:
        st.warning("Upload resume first")
