import streamlit as st
import os
import requests

API_URL = "https://stetho-api-700547311232.europe-west1.run.app/predict"

st.set_page_config(page_title="Smart Stethoscope", page_icon="🫁")

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
        opacity: 0.85;
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
        color: #a64d79;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .section-space {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }

    a {
        color: #a64d79;
        text-decoration: none;
        font-weight: 500;
    }

    a:hover {
        text-decoration: underline;
    }

    .streamlit-expanderHeader {
        color: #1f2a2e;
        font-weight: 600;
    }

    .streamlit-expanderHeader:hover {
        color: #a64d79;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ----------

# --- HEADER ---

col_title, col_logo = st.columns([3, 1])

with col_title:
    st.markdown('<h1 class="main-title">Smart Stethoscope</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Upload a respiratory audio file and enter breathing start and end time to get a prediction.</p>', unsafe_allow_html=True)

with col_logo:
    logo_path = "logo_woozle.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    else:
        pass # if image doesnt exist #Added Ant

#st.markdown(
#    """
#    <div class="app-title">Smart Stethoscope</div>
#    <div class="app-subtitle">
#        Upload a respiratory audio file, select a breath window, and run a prediction.
#    </div>
#    <div class="title-divider"></div>
#    """,
#   unsafe_allow_html=True,
#)

# ---------- Input section ----------
st.markdown('<div class="section-space">', unsafe_allow_html=True)

# Upload both required files
audio_file = st.file_uploader("Upload respiratory audio (.wav)", type=["wav"])
columns = st.columns(2)
start = columns[0].number_input("Breath start (seconds)", min_value=0.0, format="%.3f")
columns[0].write(start)
end = columns[1].number_input("Breath end (seconds)", min_value=0.0, format="%.3f")
columns[1].write(end)

# State length of selected audio window
st.caption(f"Selected window: {start:.3f}s to {end:.3f}s")

st.markdown("</div>", unsafe_allow_html=True)


# ---------- Action ----------
# Optional: play the uploaded audio in the UI
if audio_file is not None:
    st.audio(audio_file)


# ---------- Action ----------
run_prediction = st.button("Run prediction")

if run_prediction:
    # Validate inputs before calling API
    if audio_file is None:
        st.error("Please upload a .wav audio file before running the prediction.")
    elif end <= start:
        st.error("End time must be greater than start time.")
    else:
        # Prepare the file for the FastAPI backend
        files = {
            "audio_file": (audio_file.name, audio_file.getvalue(), "audio/wav"),
        }

        # Prepare the form data for the selected breath window
        data = {
            "start": start,
            "end": end,
        }

        try:
            # Spinner while waiting for the API
            with st.spinner("Running prediction..."):
                response = requests.post(
                    API_URL,
                    files=files,
                    data=data,
                    timeout=120,
                )

            # Only show success UI when the API actually returns 200
            if response.status_code == 200:
                result = response.json()

                # Pull values out of the response safely
                prediction = result.get("prediction", "Unknown")
                final_proba = result.get("final_proba", {})

                # Try to calculate confidence from the probabilities if possible
                confidence_text = "Confidence unavailable"

                if isinstance(final_proba, list) and len(final_proba) > 0:
                    #top_label, top_score = max(final_proba.items(), key=lambda x: x[1])
                    top_score = max(final_proba)
                    confidence_text = f"{top_score:.1%} confidence"


                st.success("Prediction complete")

                # PREDICTION RESULT
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-label">Prediction</div>
                        <div class="result-prediction">{prediction['predicted_label']}</div>
                        <div class="result-confidence">{confidence_text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.caption("This result reflects patterns in the data and should not be interpreted as a medical diagnosis.")

                st.markdown("<br>", unsafe_allow_html=True)

                st.subheader("Understanding your result")

                with st.expander("About the conditions we assess"):

                    st.markdown("A brief overview of the respiratory conditions included in this analysis:")

                    st.markdown("""
                    **Bronchiectasis**: A long-term condition where the airways become widened and inflamed.
                    🔗 [Learn more](https://www.mayoclinic.org/diseases-conditions/bronchiectasis/symptoms-causes/syc-20351190)

                    **COPD**: A chronic lung condition that causes breathing difficulties.
                    🔗 [Learn more](https://www.who.int/news-room/fact-sheets/detail/chronic-obstructive-pulmonary-disease-(copd))

                    **Pneumonia** — An infection that inflames the lungs, often causing cough and fever.
                    🔗 [Learn more](https://www.who.int/news-room/fact-sheets/detail/pneumonia)

                    **URTI** — An upper respiratory tract infection, like a cold or sinus infection.
                    🔗 [Learn more](https://www.ncbi.nlm.nih.gov/books/NBK532961/)

                     **Healthy** — No clear signs of a respiratory condition detected.
                    """)

                    st.caption("If you have concerns about your symptoms, we recommend speaking to a GP.")

                # Show probabilities
                with st.expander("How this result was calculated"):

                    st.caption(
                        "This shows how closely your audio sample matched patterns associated with each condition."
                    )
                    st.caption(
                        "These percentages reflect relative likelihoods, **not** a confirmed diagnosis."
                    )

                    if isinstance(prediction['class_probabilities'], dict) and len(prediction['class_probabilities']) > 0:
                        # Sort probabilities highest first
                        sorted_proba = sorted(
                            prediction['class_probabilities'].items(),
                            key=lambda x: x[1],
                            reverse=True
                        )

                        # Show one line per class
                        for label, score in sorted_proba:
                            st.write(f"**{label}:** {score:.1%}")

                    else:
                        # Fallback in case the API returns a different structure
                        st.write(final_proba)

            else:
                # Simple error message
                # With technical info underneath for debugging
                st.error("The API returned an error.")

                with st.expander("Technical details"):
                    st.write(f"Status code: {response.status_code}")
                    st.write("Response text:")
                    st.write(response.text)
                    st.write("Response headers:")
                    st.write(dict(response.headers))

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
