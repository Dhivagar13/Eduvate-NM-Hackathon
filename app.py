import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

# Load color dataset with debug info
@st.cache_data
def load_colors():
    df = pd.read_csv("colors.csv")
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces in column names
    st.write("Loaded DataFrame:", df.head())  # Print the first few rows of the DataFrame
    return df
   

def get_compatible_columns(df):
    # Lowercase column names for flexible matching
    lower_cols = [col.lower() for col in df.columns]

    # Possible expected names for R,G,B and color name columns
    r_col = next((col for col in df.columns if col.lower() == 'r'), None)
    g_col = next((col for col in df.columns if col.lower() == 'g'), None)
    b_col = next((col for col in df.columns if col.lower() == 'b'), None)
    color_col = next((col for col in df.columns if 'color' in col.lower() and 'name' in col.lower()), None)

    missing = []
    if r_col is None: missing.append("R")
    if g_col is None: missing.append("G")
    if b_col is None: missing.append("B")
    if color_col is None: missing.append("color_name")

    if missing:
        st.error(f"Missing columns in colors.csv: {', '.join(missing)}")
        return None, None, None, None

    return r_col, g_col, b_col, color_col

def get_closest_color_name(R, G, B, df, r_col, g_col, b_col, color_col):
    min_dist = float('inf')
    closest_color = ""
    for i in range(len(df)):
        d = abs(R - int(df.loc[i, r_col])) + abs(G - int(df.loc[i, g_col])) + abs(B - int(df.loc[i, b_col]))
        if d < min_dist:
            min_dist = d
            closest_color = df.loc[i, color_col]
    return closest_color

def main():
    st.title("🎨 Color Detection from Image")
    st.write("Upload an image and enter pixel coordinates to detect the color name and RGB values.")

    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if not uploaded_file:
        st.info("Please upload an image to start.")
        return

    image = Image.open(uploaded_file).convert('RGB')
    image_np = np.array(image)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    df = load_colors()
    st.write("Color dataset columns detected:", df.columns.tolist())

    r_col, g_col, b_col, color_col = get_compatible_columns(df)
    if None in [r_col, g_col, b_col, color_col]:
        st.stop()

    st.write("Enter pixel coordinates to detect color:")
    col1, col2 = st.columns(2)
    with col1:
        x = st.number_input("X Coordinate", min_value=0, max_value=image_np.shape[1]-1, step=1)
    with col2:
        y = st.number_input("Y Coordinate", min_value=0, max_value=image_np.shape[0]-1, step=1)

    if st.button("Detect Color"):
        pixel = image_np[int(y), int(x)]
        R, G, B = int(pixel[0]), int(pixel[1]), int(pixel[2])
        color_name = get_closest_color_name(R, G, B, df, r_col, g_col, b_col, color_col)

        st.markdown(f"**Color Name:** {color_name}")
        st.markdown(f"**RGB:** ({R}, {G}, {B})")

        st.markdown("### Detected Color:")
        st.markdown(
            f"<div style='width:100px;height:100px;background-color:rgb({R},{G},{B});border-radius:10px'></div>",
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    main()
