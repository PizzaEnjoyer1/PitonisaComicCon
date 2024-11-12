import os
import streamlit as st
import base64
from openai import OpenAI
import openai
#from PIL import Image
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_drawable_canvas import st_canvas

Expert=" "
profile_imgenh=" "
    
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# Streamlit 
st.set_page_config(page_title='Tablero Inteligente')
st.title('Tablero Inteligente')
with st.sidebar:

  st.title("Cambia los parámetros de tu canvas")
  
  drawing_mode = st.selectbox(
    "Selecciona el modo de dibujo",
    ("freedraw", "line", "transform", "rect", "circle")
  )


  stroke_width = st.slider("Grosor del pincel", 1, 100, 10)

  stroke_color = st.color_picker("Selecciona el color de linea", "#000000")

  fill_color = st.color_picker("Selecciona el color de relleno", "#000000")
  
  bg_color = st.color_picker("Selecciona el color del fondo", "#FFFFFF")


name = st.text_input("Escribe tu nombre, aventurero")

# Inicializamos la variable para almacenar la opción seleccionada
selected_class = None


st.subheader("Selecciona tu clase:")

# Creamos 4 columnas para organizar los botones de forma horizontal
col1, col2, col3, col4 = st.columns(4)


# Agrega botones en cada columna con iconos y define el valor que se almacena según la selección
with col1:
    if st.button("🏠 Opción 1"):
        selected_class = "Opción 1"

with col2:
    if st.button("🔍 Opción 2"):
        selected_class = "Opción 2"

with col3:
    if st.button("📈 Opción 3"):
        selected_class = "Opción 3"

with col4:
    if st.button("⚙️ Opción 4"):
        selected_class = "Opción 4"

# Mostrar el valor almacenado para confirmar la selección
if selected_class:
    st.write(f"Has seleccionado: {selected_class}")

prompt = st.text_input("Escribe lo que quieras saber de la imagen")

st.subheader("Dibuja el acompañante que tendrás en tu viaje")


# Create a canvas component
canvas_result = st_canvas(
    fill_color=fill_color,  # Fixed fill color with some opacity
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=720,
    width=1280,
    #background_image= None #Image.open(bg_image) if bg_image else None,
    drawing_mode=drawing_mode,
    key="canvas",
)

ke = st.text_input('Ingresa tu Clave')
#os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['OPENAI_API_KEY'] = ke


# Retrieve the OpenAI API Key from secrets
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

analyze_button = st.button("Crea tu historia", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('img.png')
        
      # Codificar la imagen en base64
 
        base64_image = encode_image_to_base64("img.png")
            
        prompt_text = (f"Describe briefly the image, and tell me a childish story about it in Spanish")
    
      # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url":f"data:image/png;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
              model= "gpt-4o-mini",  #o1-preview ,gpt-4o-mini
              messages=[
                {
                   "role": "user",
                   "content": [
                     {"type": "text", "text": prompt_text},
                     {
                       "type": "image_url",
                       "image_url": {
                         "url": f"data:image/png;base64,{base64_image}",
                       },
                     },
                   ],
                  }
                ],
              max_tokens=500,
              )
            #response.choices[0].message.content
            if response.choices[0].message.content is not None:
                    full_response += response.choices[0].message.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
            if Expert== profile_imgenh:
               st.session_state.mi_respuesta= response.choices[0].message.content #full_response 
    
            # Display the response in the app
            #st.write(response.choices[0])
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required

    if not api_key:
        st.warning("Por favor ingresa tu API key.")

