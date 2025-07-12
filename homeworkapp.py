import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from openai import OpenAI

# -------------------------------
# Streamlit Config
# -------------------------------
st.set_page_config(page_title="Homework Assistant", layout="centered")

# -------------------------------
# Title
# -------------------------------
st.title("📚 Homework Assistant")

st.write(
    """
    Hello! 👋  
    This app helps you read questions from your book or notebook  
    and provides helpful, **concise** answers for your child's homework.
    
    **How to use:**  
    - Take a photo of the page OR upload an image  
    - The app reads text from your image  
    - It shows you short answers, and lets you request an explanation!
    """
)

# -------------------------------
# OpenAI API Key from secrets
# -------------------------------
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("Please set your OPENAI_API_KEY in .streamlit/secrets.toml.")
    st.stop()

# -------------------------------
# User Options
# -------------------------------
option = st.radio(
    "How would you like to provide the questions?",
    ("📷 Take a Photo", "📁 Upload an Image"),
)

image = None

if option == "📷 Take a Photo":
    img_file = st.camera_input("Take a photo of the book or notebook")
    if img_file is not None and img_file.size > 0:
        image = Image.open(img_file)

elif option == "📁 Upload an Image":
    uploaded_file = st.file_uploader(
        "Upload a photo or screenshot",
        type=["png", "jpg", "jpeg"],
    )
    if uploaded_file is not None and uploaded_file.size > 0:
        image = Image.open(uploaded_file)

# -------------------------------
# Process Image if Present
# -------------------------------
if image is not None:
    st.subheader("Scanned Image Preview")
    st.image(image, use_container_width=True)

    st.subheader("🔎 Extracting Text...")

    img_np = np.array(image)

    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(img_np, detail=0, paragraph=True)
    extracted_text = "\n".join(results)

    if extracted_text.strip() == "":
        st.warning("No text was detected in the image. Please try again with a clearer photo.")
    else:
        st.success("Text Detected:")
        st.text_area("Extracted Text", value=extracted_text, height=200)

        # Split into lines for question/answer display
        questions = [line.strip() for line in extracted_text.split("\n") if line.strip()]

        if questions:
            st.subheader("📖 Questions and Answers")

            for idx, question in enumerate(questions, start=1):
                st.markdown(f"**Q{idx}. {question}**")

                # Get short answer
                with st.spinner("Thinking..."):
                    try:
                        short_prompt = f"Answer this question for a child in grades 3-5 in a single sentence, no extra explanation: {question}"

                        completion = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a helpful homework assistant for children aged 8-11. Provide short, factual answers suitable for a child in grades 3-5. Do not elaborate unless asked."
                                },
                                {
                                    "role": "user",
                                    "content": short_prompt
                                }
                            ],
                            temperature=0.3,
                            max_tokens=100,
                        )

                        short_answer = completion.choices[0].message.content.strip()

                    except Exception as e:
                        short_answer = f"Sorry, I couldn't fetch an answer. Error: {e}"

                st.write(f"✅ **Answer:** {short_answer}")

                # Button to get a longer explanation
                expander = st.expander("🔎 Explain More")
                with expander:
                    if st.button(f"Get Explanation for Q{idx}", key=f"explain_{idx}"):
                        with st.spinner("Generating detailed explanation..."):
                            try:
                                long_prompt = f"Explain this in detail for a child in grades 3-5: {question}"

                                long_completion = client.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {
                                            "role": "system",
                                            "content": "You are a helpful homework assistant for children aged 8-11. Provide detailed but simple explanations suitable for a child in grades 3-5."
                                        },
                                        {
                                            "role": "user",
                                            "content": long_prompt
                                        }
                                    ],
                                    temperature=0.4,
                                    max_tokens=300,
                                )

                                long_answer = long_completion.choices[0].message.content.strip()

                            except Exception as e:
                                long_answer = f"Sorry, I couldn't fetch an explanation. Error: {e}"

                        st.write(f"📖 **Explanation:** {long_answer}")

        else:
            st.info("No specific questions detected in the extracted text.")
else:
    st.info("Please upload an image or take a photo to begin.")
