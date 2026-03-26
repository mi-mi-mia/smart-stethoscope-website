import streamlit as st
import requests

API_URL = "https://stetho-api-700547311232.europe-west1.run.app/predict"

st.set_page_config(page_title="Smart Stethoscope", page_icon="🫁")

st.title("Smart Stethoscope")
st.write(
    "Upload a respiratory audio file and enter breathing start and end time to get a prediction."
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #f3f5f4;
        color: #1f2a2e;
    }

    .main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        color: #1f2a2e;
        margin-bottom: 0.4rem;
        line-height: 1;
    }

    .subtitle {
        color: #4f5b60;
        font-size: 1.1rem;
        margin-bottom: 2.2rem;
        max-width: 720px;
    }

    .section-label {
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        color: #2f7f7b;
        text-transform: uppercase;
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
    }

    .prediction-label {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #1f2a2e;
        margin-bottom: 0.2rem;
    }

    .small-muted {
        color: #5f6a6f;
        font-size: 0.95rem;
    }

    /* soften default spacing a bit */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Upload both required files
audio_file = st.file_uploader("Upload audio file (.wav)", type=["wav"])
columns = st.columns(2)
start = columns[0].number_input("Start time of the breath recording", format="%.3f")
columns[0].write(start)
end = columns[1].number_input("End time of the breath recording", format="%.3f")
columns[1].write(end)

# Optional: play the uploaded audio in the UI
if audio_file is not None:
    st.audio(audio_file)

if st.button("Run prediction"):
    if audio_file is None:
        st.error("Please upload an audio file.")
    elif end <= start:
        st.error("End time must be greater than start time.")
    else:
        files = {
            "audio_file": (audio_file.name, audio_file.getvalue(), "audio/wav"),
        }

        data = {
            "start": start,
            "end": end,
        }

        try:
            with st.spinner("Sending data to API and running prediction..."):
                response = requests.post(
                    API_URL,
                    files=files,
                    data=data,
                    timeout=120,
                )

            st.write(f"Status code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()

                st.success("Prediction complete")
                st.subheader("Result")

                st.write(f"**Prediction:** {result['prediction']}")

                st.subheader("Model probabilities")
                st.write(f"Final probabilities: {result['final_proba']}")

            else:
                st.error("The API returned an error.")
                st.write("Response text:")
                st.write(response.text)
                st.write("Response headers:")
                st.write(dict(response.headers))

        except requests.exceptions.Timeout:
            st.error("The request timed out.")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
