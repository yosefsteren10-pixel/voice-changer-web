import streamlit as st
import os
from spleeter.separator import Separator
import librosa
import soundfile as sf
import numpy as np

# הגדרת הדף
st.set_page_config(page_title="עורך קול זמר", page_icon="🎤")

st.title("🎤 הפרדת זמר ושינוי גובה קול")
st.write("העליתי הכל מהדפדפן! העלה שיר כדי להתחיל.")

# יצירת תיקיות זמניות
os.makedirs("temp", exist_ok=True)
os.makedirs("output", exist_ok=True)

uploaded_file = st.file_uploader("בחר שיר (MP3/WAV)", type=["mp3", "wav"])
pitch_steps = st.slider("שינוי גובה הקול (Semis)", min_value=-12, max_value=12, value=0)

if uploaded_file is not None:
    if st.button("בצע קסם ✨"):
        with st.spinner('מפריד את הקול מהמוזיקה... (לוקח כדקה)'):
            # שמירה זמנית
            file_path = os.path.join("temp", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # הפרדה
            separator = Separator('spleeter:2stems')
            separator.separate_to_file(file_path, "output")

            # נתיבים
            filename_no_ext = os.path.splitext(uploaded_file.name)[0]
            vocals_path = os.path.join("output", filename_no_ext, "vocals.wav")
            accompaniment_path = os.path.join("output", filename_no_ext, "accompaniment.wav")

        with st.spinner('משנה את קול הזמר ומחבר מחדש...'):
            # טעינה ושינוי פיץ'
            y_vocals, sr = librosa.load(vocals_path, sr=None)
            y_shifted_vocals = librosa.effects.pitch_shift(y_vocals, sr=sr, n_steps=pitch_steps)

            # טעינת ליווי
            y_accomp, _ = librosa.load(accompaniment_path, sr=sr)

            # חיתוך לאורך זהה
            min_len = min(len(y_shifted_vocals), len(y_accomp))
            y_combined = y_shifted_vocals[:min_len] + y_accomp[:min_len]

            # שמירה
            final_output = "final_result.wav"
            sf.write(final_output, y_combined, sr)

        st.success("מוכן!")
        st.audio(final_output)
        
        with open(final_output, "rb") as f:
            st.download_button("הורד תוצאה", f, "remix.wav", "audio/wav")
