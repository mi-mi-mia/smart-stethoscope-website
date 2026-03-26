import streamlit as st
import requests

API_URL = "https://stetho-api-700547311232.europe-west1.run.app/predict"

st.set_page_config(page_title="Smart Stethoscope", page_icon="🫁")

st.title("Smart Stethoscope")
st.write(
    "Upload a respiratory audio file and enter breathing start and end time to get a prediction."
)

# ---------- Styling ----------
# Keep this light-touch and safe:
# - soft blue background to match the deck
# - dark charcoal text for headings
# - thin teal divider
# - very subtle result block styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #e9eef0;
    }

    .app-title {
        color: #1f2a2e;
        font-size: 3rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 0.25rem;
    }

    .app-subtitle {
        color: #36454f;
        font-size: 1rem;
        margin-bottom: 1rem;
    }

    .title-divider {
        width: 100%;
        height: 3px;
        background-color: #4f9da6;  /* muted teal */
        border-radius: 999px;
        margin: 0.5rem 0 2rem 0;
    }

    .result-card {
        background-color: rgba(255, 255, 255, 0.45);
        border: 1px solid rgba(79, 157, 166, 0.35);  /* soft teal border */
        border-radius: 12px;
        padding: 1rem 1rem 0.75rem 1rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .result-label {
        color: #4f9da6;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.35rem;
    }

    .result-prediction {
        color: #1f2a2e;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .result-confidence {
        color: #7d5a78;  /* muted pink-plum accent */
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .section-space {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ----------
# Using a small HTML block here gives you better visual hierarchy
# without needing to heavily style Streamlit components.
st.markdown(
    """
    <div class="app-title">Smart Stethoscope</div>
    <div class="app-subtitle">
        Upload a respiratory audio file, select a breath window, and run a prediction.
    </div>
    <div class="title-divider"></div>
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
