import streamlit as st
from PIL import Image
import pytesseract

# ----------------------------------------
# OPTIONAL: Explicitly set Tesseract path
# Uncomment and adjust if needed on Windows
# ----------------------------------------
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -------------------------------
# Streamlit App Config
# -------------------------------
st.set_page_config(page_title="Homework Assistant", layout="centered")

# -------------------------------
# Title and Instructions
# -------------------------------
st.title("📚 Homework Assistant")

st.write(
    """
    Hello! 👋  
    This app helps you read questions from your book or notebook  
    and provides simple help for your child's homework.
    
    **How to use:**  
    - Take a photo of the page OR upload an image  
    - The app will read the text from your image  
    - It will show you the questions and some simple answers
    """
)

# -------------------------------
# Input Options
# -------------------------------
option = st.radio(
    "How would you like to provide the questions?",
    ("📷 Take a Photo", "📁 Upload an Image"),
)

image = None

if option == "📷 Take a Photo":
    img_file = st.camera_input("Take a photo of the book or notebook")
    if img_file is not None and img_file.size > 0:
        try:
            image = Image.open(img_file)
        except Exception as e:
            st.error(f"Error reading image: {e}")
    else:
        st.info("No photo captured yet. Please take a picture to continue.")

elif option == "📁 Upload an Image":
    uploaded_file = st.file_uploader(
        "Upload a photo or screenshot",
        type=["png", "jpg", "jpeg"],
    )
    if uploaded_file is not None and uploaded_file.size > 0:
        try:
            image = Image.open(uploaded_file)
        except Exception as e:
            st.error(f"Error reading image: {e}")
    else:
        st.info("Please upload a valid image file.")

# -------------------------------
# Process Image if Present
# -------------------------------
if image is not None:
    st.subheader("Scanned Image Preview")
    st.image(image, use_container_width=True)

    st.subheader("🔎 Extracting Text...")

    # Run OCR
    extracted_text = pytesseract.image_to_string(image)

    if extracted_text.strip() == "":
        st.warning("No text was detected in the image. Please try again with a clearer photo.")
    else:
        st.success("Text Detected:")
        st.text_area("Extracted Text", value=extracted_text, height=200)

        # Split into lines for question/answer display
        questions = [line.strip() for line in extracted_text.split("\n") if line.strip()]

        if questions:
            st.subheader("📖 Questions and Simple Answers")

            for idx, question in enumerate(questions, start=1):
                st.markdown(f"**Q{idx}. {question}**")

                # Simple placeholder answer logic
                answer = f"This is a simple answer for: '{question}'"
                st.write(f"✅ **Answer:** {answer}")
        else:
            st.info("No specific questions detected in the extracted text.")
else:
    st.info("Please upload an image or take a photo to begin.")
