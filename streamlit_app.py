import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

def add_logo_and_text(background, logo, org_name):
    # Resize background to 1290x192
    bg_resized = background.resize((1290, 192))

    # Ensure the logo has an alpha channel
    if logo.mode != "RGBA":
        logo = logo.convert("RGBA")

    # Calculate logo size and position
    logo_width, logo_height = logo.size
    max_logo_height = 192 - 24  # Considering 12 pixels padding from top and bottom
    if logo_height > max_logo_height:
        logo_ratio = max_logo_height / logo_height
        logo_width = int(logo_width * logo_ratio)
        logo_height = max_logo_height
    logo_resized = logo.resize((logo_width, logo_height))

    # Positioning logo
    logo_x = 12
    logo_y = 12

    # Paste logo on the background
    bg_resized.paste(logo_resized, (logo_x, logo_y), logo_resized)

    # Add organization name text
    draw = ImageDraw.Draw(bg_resized)
    font_size = 40
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text_x = logo_x + logo_width + 30
    text_y = (192 - font_size) // 2
    draw.text((text_x, text_y), org_name, font=font, fill="white")

    return bg_resized

st.title("Image Generator")

uploaded_background = st.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"])
uploaded_logo = st.file_uploader("Upload Logo Image", type=["png", "jpg", "jpeg"])
org_name = st.text_input("Enter Organization Name")

if uploaded_background and uploaded_logo and org_name:
    background = Image.open(uploaded_background)
    logo = Image.open(uploaded_logo)

    result_image = add_logo_and_text(background, logo, org_name)

    # Display the result image
    st.image(result_image, caption="Generated Image")

    # Prepare the image for download
    buf = io.BytesIO()
    result_image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(label="Download Image", data=byte_im, file_name="output.png", mime="image/png")
