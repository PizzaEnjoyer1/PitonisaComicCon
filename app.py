import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import time
import glob
#from PIL import Image
import tensorflow as tf
from gtts import gTTS
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
st.set_page_config(page_title='Pitonisa Imperial')
st.title('Pitonisa Imperial: Descubre tu destino')
st.image("pitonisa.jpg")
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


st.text("Selecciona tu clase:")

# Creamos 4 columnas para organizar los botones de forma horizontal
col1, col2, col3, col4, col5 = st.columns(5)


# Agrega botones en cada columna con iconos y define el valor que se almacena según la selección

selected_class = ""

with col1:
    if st.button("🛡️ Paladín"):
        selected_class = "Paladín"

with col2:
    if st.button("🧙 Mago"):
        selected_class = "Mago"

with col3:
    if st.button("🏹 Arquero"):
        selected_class = "Arquero"

with col4:
    if st.button("🗡️ Caballero"):
        selected_class = "Caballero"

with col5:
    if st.button("🩹 Curandero"):
        selected_class = "Curandero"

# Mostrar el valor almacenado para confirmar la selección
if selected_class != None and name != None:
    st.write(f"{name}, has seleccionado: {selected_class}")

else:
    st.write("Por favor, escribe tu nombre")
    


st.text("Dibuja el acompañante que tendrás en tu viaje")


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

os.environ['OPENAI_API_KEY'] = ke

# Retrieve the OpenAI API Key from secrets
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

analyze_button = st.button("Crea tu historia", type="secondary")

def text_to_speech(text, lg):
    tts = gTTS(text, lang=lg)
    try:
        my_file_name = text[:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, text

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Creando tu historia ..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('img.png')
        
      # Codificar la imagen en base64
 
        base64_image = encode_image_to_base64("img.png")
            
        prompt_text = (f"Comenzarás la historia así: {name} es un/a {selected_class}. En la imagen, logras ver su compañero de aventuras. Con base a esta información, haz una historia fantástica ambientada en la edad media")
    
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

# Botón para convertir el texto a audio
if st.button("Convertir a Audio"):
    if full_response.strip() != "":  # Usamos full_response como el texto generado por la IA
        # Muestra el texto generado
        st.subheader("Texto generado:")
        st.write(full_response)

        # Crea un contenedor vacío para el GIF de carga
        gif_placeholder = st.empty()

        # Inserta el GIF de carga en el contenedor vacío
        with gif_placeholder:
            st.markdown(
                f'<img src="data:image/gif;base64,{base64.b64encode(open(loading_gif, "rb").read()).decode()}" width="100" alt="Loading...">',
                unsafe_allow_html=True
            )
        
        # Simula el tiempo de procesamiento (ajustable si es necesario)
        time.sleep(2)  
        
        # Conversión del texto a audio (en español)
        result, output_text = text_to_speech(full_response, 'es')
        
        # Una vez que termina el procesamiento, vacía el contenedor del GIF
        gif_placeholder.empty()
        
        # Cargar y reproducir el archivo de audio generado
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        # Descargar archivo de audio
        with open(f"temp/{result}.mp3", "rb") as f:
            data = f.read()

        def get_binary_file_downloader_html(bin_file, file_label='Audio File'):
            bin_str = base64.b64encode(data).decode()
            href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
            return href

        st.markdown(get_binary_file_downloader_html(f"temp/{result}.mp3", "Audio File"), unsafe_allow_html=True)

else:
    st.write("XD")

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400  # Convertir los días a segundos
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

# Llamada a la función para eliminar archivos de más de 7 días
remove_files(7)
