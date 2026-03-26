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
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Upload both required files
audio_file = st.file_uploader("Upload audio file (.wav)", type=["wav"])
columns = st.columns(2)
start = columns[0].number_input("Start time of the breath recording (in seconds)", format="%.3f")
columns[0].write(start)
end = columns[1].number_input("End time of the breath recording (in seconds)", format="%.3f")
columns[1].write(end)
st.write(f"The current length of the audio to be analyzed is: {end - start} seconds")

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

                st.write(f"**Prediction:** {result['prediction']['predicted_label']}")

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
