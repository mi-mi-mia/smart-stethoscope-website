import streamlit as st
import requests

# Your deployed FastAPI endpoint
API_URL = "https://stetho-api-700547311232.europe-west1.run.app/predict"

# Keep page config near the top
st.set_page_config(
    page_title="Smart Stethoscope",
    page_icon="🫁",
)

# ---------- Styling ----------
# Light-touch styling only:
# - soft blue background
# - dark charcoal headings
# - teal divider
# - subtle result card
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
        background-color: #4f9da6;
        border-radius: 999px;
        margin: 0.5rem 0 2rem 0;
    }

    .result-card {
        background-color: rgba(255, 255, 255, 0.45);
        border: 1px solid rgba(79, 157, 166, 0.35);
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
        color: #7d5a78;
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
# Custom header block replaces the default Streamlit title
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

# ---------- Input section ----------
st.markdown('<div class="section-space">', unsafe_allow_html=True)

# File upload
audio_file = st.file_uploader(
    "Upload respiratory audio (.wav)",
    type=["wav"]
)

# Start/end inputs in two columns
col1, col2 = st.columns(2)

start = col1.number_input(
    "Breath start (seconds)",
    min_value=0.0,
    format="%.3f"
)

end = col2.number_input(
    "Breath end (seconds)",
    min_value=0.0,
    format="%.3f"
)

# IMPORTANT:
# We do NOT write out start/end underneath the inputs,
# because those lines created the little green number boxes.
# So these old lines should stay deleted:
# col1.write(start)
# col2.write(end)

# Show selected window in a calmer, cleaner way
st.caption(f"Selected window: {start:.3f}s to {end:.3f}s")

st.markdown("</div>", unsafe_allow_html=True)

# ---------- Audio preview ----------
# Helpful for demo reassurance
if audio_file is not None:
    st.audio(audio_file)

# ---------- Action ----------
run_prediction = st.button("Run prediction")

# Small spacer so the feedback area sits a bit lower
st.markdown("<br>", unsafe_allow_html=True)

# This container anchors all feedback/results below the button
result_container = st.container()

if run_prediction:
    # Everything shown after clicking the button
    # now appears in this same consistent place
    with result_container:

        # Validate inputs before calling the API
        if audio_file is None:
            st.error("Please upload a .wav audio file before running the prediction.")

        elif end <= start:
            st.error("End time must be greater than start time.")

        else:
            # Prepare uploaded file for FastAPI
            files = {
                "audio_file": (audio_file.name, audio_file.getvalue(), "audio/wav"),
            }

            # Prepare selected time window for FastAPI
            data = {
                "start": start,
                "end": end,
            }

            try:
                # Show spinner while waiting
                with st.spinner("Running prediction..."):
                    response = requests.post(
                        API_URL,
                        files=files,
                        data=data,
                        timeout=120,
                    )

                # ---------- Successful API response ----------
                if response.status_code == 200:
                    result = response.json()

                    st.success("Prediction complete")

                    # Extract fields from current API response structure
                    prediction = result.get("predicted_label", "Unknown")
                    confidence = result.get("confidence", None)
                    class_probs = result.get("class_probabilities", {})

                    # Confidence text for the result card
                    if confidence is not None:
                        confidence_text = f"{confidence:.1%} confidence"
                    else:
                        confidence_text = "Confidence unavailable"

                    # Main result card
                    st.markdown(
                        f"""
                        <div class="result-card">
                            <div class="result-label">Top prediction</div>
                            <div class="result-prediction">{prediction}</div>
                            <div class="result-confidence">{confidence_text}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Show next most likely classes, if available
                    sorted_probs = []

                    if isinstance(class_probs, dict) and len(class_probs) > 0:
                        # Sort highest probability first
                        sorted_probs = sorted(
                            class_probs.items(),
                            key=lambda x: x[1],
                            reverse=True
                        )

                        # Remove top prediction from alternatives list
                        other_classes = [
                            (label, score)
                            for label, score in sorted_probs
                            if label != prediction
                        ]

                        # Only show top 2 alternatives
                        other_classes = other_classes[:2]

                        if len(other_classes) > 0:
                            st.subheader("Other possible classes")

                            for label, score in other_classes:
                                st.write(f"**{label}:** {score:.1%}")

                    # Keep full probabilities tucked away for transparency
                    with st.expander("All class probabilities"):
                        if isinstance(class_probs, dict) and len(sorted_probs) > 0:
                            for label, score in sorted_probs:
                                st.write(f"**{label}:** {score:.3f}")
                        else:
                            st.write(class_probs)

                    # Demo-safe note
                    st.caption(
                        "This model output is for demonstration purposes only and is not a medical diagnosis."
                    )

                # ---------- API returned non-200 ----------
                else:
                    st.error("Something went wrong while running the prediction. Please try again.")

                    with st.expander("Technical details"):
                        st.write(f"Status code: {response.status_code}")
                        st.write("Response text:")
                        st.write(response.text)
                        st.write("Response headers:")
                        st.write(dict(response.headers))

            # ---------- Timeout ----------
            except requests.exceptions.Timeout:
                st.error("The request timed out. Please try again.")

            # ---------- Other request error ----------
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
