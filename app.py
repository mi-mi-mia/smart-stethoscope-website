import streamlit as st
import requests

API_URL = "https://stetho-api-248800634185.europe-west1.run.app/predict"

st.set_page_config(page_title="Smart Stethoscope", page_icon="🫁")

st.title("Smart Stethoscope")
st.write("Upload a respiratory audio file and its annotation file to get a prediction.")

# Upload both required files
audio_file = st.file_uploader("Upload audio file (.wav)", type=["wav"])
#annotation_file = st.file_uploader("Upload annotation file (.txt)", type=["txt"])
start = st.number_input('Input start time of the breath recording')
end = st.number_input('input stop time of the breath recording')

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
                st.write(f"**Prediction (class id):** {result['final_prediction_int']}")

                st.subheader("Model probabilities")
                st.write(f"Final probabilities: {result['final_proba']}")

                st.subheader("Chunk-level outputs")
                st.write("XGB:", result["xgb_chunk_proba"])
                st.write("CNN:", result["cnn_chunk_proba"])
                st.write("Fused:", result["fused_chunk_proba"])

            else:
                st.error("The API returned an error.")
                st.text(response.text)

        except requests.exceptions.Timeout:
            st.error("The request timed out.")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
