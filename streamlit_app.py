import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import pandas as pd
import requests
from io import BytesIO

def add_logo_and_text(background, logo, org_name, font_size):
    # Calculate the aspect ratio
    bg_width, bg_height = background.size
    target_width = 1290
    target_height = 192
    aspect_ratio = bg_width / bg_height

    # Scale to fit the width
    new_height = int(target_width / aspect_ratio)
    bg_resized = background.resize((target_width, new_height))

    # Crop equally from top and bottom
    top_crop = (new_height - target_height) // 2
    bottom_crop = top_crop + target_height
    bg_cropped = bg_resized.crop((0, top_crop, target_width, bottom_crop))

    # Ensure the background image has an alpha channel
    if bg_cropped.mode != "RGBA":
        bg_cropped = bg_cropped.convert("RGBA")

    # Ensure the logo has an alpha channel
    if logo.mode != "RGBA":
        logo = logo.convert("RGBA")

    # Calculate logo size and position
    logo_width, logo_height = logo.size
    max_logo_height = target_height - 24  # Considering 12 pixels padding from top and bottom
    if logo_height > max_logo_height:
        logo_ratio = max_logo_height / logo_height
        logo_width = int(logo_width * logo_ratio)
        logo_height = max_logo_height
    logo_resized = logo.resize((logo_width, logo_height))

    # Positioning logo
    logo_x = 12
    logo_y = 12

    # Paste logo on the background
    bg_cropped.paste(logo_resized, (logo_x, logo_y), logo_resized)

    # Add organization name text
    draw = ImageDraw.Draw(bg_cropped)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text_x = logo_x + logo_width + 30
    text_y = (target_height - font_size) // 2
    draw.text((text_x, text_y), org_name, font=font, fill="white")

    return bg_cropped

def fetch_image_from_url(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def process_batch(excel_file, font_size):
    df = pd.read_excel(excel_file)
    images = []
    for index, row in df.iterrows():
        background = fetch_image_from_url(row['TwBgImg'])
        logo = fetch_image_from_url(row['TwProfileImg'])
        org_name = row['Name']
        result_image = add_logo_and_text(background, logo, org_name, font_size)
        images.append((org_name, result_image))
    return images

st.title("Image Generator")

mode = st.radio("Select Mode", ["Solo Mode", "Batch Mode"])

if mode == "Solo Mode":
    uploaded_background = st.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"])
    uploaded_logo = st.file_uploader("Upload Logo Image", type=["png", "jpg", "jpeg"])
    org_name = st.text_input("Enter Organization Name")
    font_size = st.slider("Select Font Size", min_value=24, max_value=200, value=50)

    if uploaded_background and uploaded_logo and org_name:
        background = Image.open(uploaded_background)
        logo = Image.open(uploaded_logo)

        result_image = add_logo_and_text(background, logo, org_name, font_size)

        # Display the result image
        st.image(result_image, caption="Generated Image")

        # Prepare the image for download
        buf = io.BytesIO()
        result_image.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(label="Download Image", data=byte_im, file_name=f"{org_name}.png", mime="image/png")

elif mode == "Batch Mode":
    uploaded_excel = st.file_uploader("Upload Excel File", type=["xlsx"])
    font_size = st.slider("Select Font Size", min_value=24, max_value=200, value=50)

    if uploaded_excel:
        images = process_batch(uploaded_excel, font_size)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for org_name, image in images:
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                zip_file.writestr(f"{org_name}.png", buf.getvalue())

        st.download_button(label="Download All Images as ZIP", data=zip_buffer.getvalue(), file_name="images.zip", mime="application/zip")

        for org_name, image in images:
            st.image(image, caption=f"Generated Image for {org_name}")
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(label=f"Download {org_name}.png", data=byte_im, file_name=f"{org_name}.png", mime="image/png")
