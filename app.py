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
    .stApp {
        background-color: #e9eef0;
        color: #1f2a2e;
    }

    h1, h2, h3 {
        color: #1f2a2e;
    }

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: #1f2a2e;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #4a5a5f;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    .section-label {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #2f7f7b;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    .card {
        background-color: #f8fbfc;
        padding: 1.2rem 1.2rem 1rem 1.2rem;
        border-radius: 18px;
        border: 1px solid #d6e0e3;
        margin-bottom: 1rem;
    }

    .result-card {
        background-color: #fff7f5;
        padding: 1.2rem;
        border-radius: 18px;
        border: 1px solid #f0c8bd;
        margin-top: 1rem;
    }

    .prediction-label {
        font-size: 2rem;
        font-weight: 800;
        color: #1f2a2e;
        margin-bottom: 0.2rem;
    }

    .small-muted {
        color: #5b6a6f;
        font-size: 0.95rem;
    }

    /* -------- Force light mode overrides -------- */

    .stMarkdown, .stText, p, span, div {
        color: #1f2a2e !important;
    }

    label {
        color: #1f2a2e !important;
    }

    input, textarea {
        color: #1f2a2e !important;
        background-color: #ffffff !important;
    }

    /* Buttons */
    button {
        background-color: #2f7f7b !important;
        color: white !important;
        border-radius: 10px !important;
    }

    /* Streamlit metric styling */
    [data-testid="stMetricValue"] {
        color: #1f2a2e !important;
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
