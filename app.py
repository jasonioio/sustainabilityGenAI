import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import json
import catppuccin
from io import BytesIO

# Define the API endpoint
API_ENDPOINT = "https://wjsqyfi4n2.execute-api.us-west-2.amazonaws.com/prod/my-function"

def post_to_api(prompt):
    try:
        response = requests.post(API_ENDPOINT, json={"prompt": prompt})
        return response.json()  # Assuming the response is JSON
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Set the background image using CSS
background_image_url = "https://lachlanwetherall.com/wp-content/uploads/2014/04/WindowsXPWallpaper.jpg"  # Replace with your image URL

st.markdown(
    f"""
    <style>
    .reportview-container {{
        background-image: url('{background_image_url}');
        background-size: cover;  /* Cover the entire area */
        background-position: center;  /* Center the image */
        height: 100vh;  /* Full height */
        position: relative;  /* For layering */
    }}
    .overlay {{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(255, 255, 255, 0.7); /* Optional: semi-transparent overlay */
        z-index: 1; /* Ensures content is above background */
    }}
    .content {{
        position: relative;
        z-index: 2; /* Ensures content is above the overlay */
    }}
    </style>
    """, unsafe_allow_html=True
)

# Create a div for overlay and content
st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)

# Content area
with st.container():
    st.markdown('<div class="content">', unsafe_allow_html=True)

    # Create random cloud emojis
    clouds = "☁️" * 10  # Adjust the number of clouds as needed

    # Display cloud emojis in a fixed position
    st.markdown(f'<div style="font-size: 50px; text-align: center; margin-top: 10%;">{clouds}</div>', unsafe_allow_html=True)

    st.markdown(
    """
    <h1 style="text-align: center;">UBC Green Bot 🍃</h1>
    """, 
    unsafe_allow_html=True
    )

    # User input field
    prompt = st.text_input("Enter your prompt:")

    # Initialize session state for response
    if 'response_data' not in st.session_state:
        st.session_state.response_data = None

    # Submit button
    if st.button("Submit"):
        if prompt:
            response = post_to_api(prompt)
            st.session_state.response_data = response
            
            # Reset display
            st.session_state.display_description = None
            st.session_state.display_graph = None
            
        else:
            st.error("Please enter a prompt.")

    # Display the response if available
    if st.session_state.response_data:
        system_message = st.session_state.response_data.get('systemMessage', '{}')
        
        try:
            parsed_message = json.loads(system_message)
            description = parsed_message.get('description', '')
            array_data = parsed_message.get('array', [])
        except json.JSONDecodeError:
            description = "Error parsing the response."
            array_data = []

        st.write(description)

        if array_data:
            if len(array_data) <= 1:
                for obj in array_data:
                    for key, value in obj.items():
                        st.write(f"{key}: {value}")
            else:
                keys = []
                values = []
                
                for obj in array_data:
                    for key, value in obj.items():
                        keys.append(key)
                        values.append(value)

                df = pd.DataFrame({'Keys': keys, 'Values': values})

                # Plot the bar graph
                plt.style.use(catppuccin.PALETTE.macchiato.identifier)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.bar(df['Keys'], df['Values'], color='skyblue')
                ax.set_xlabel('Keys')
                ax.set_ylabel('Values')
                ax.set_title('Bar Graph of Response Array')
                ax.set_xticks(range(len(df['Keys'])))
                ax.set_xticklabels(df['Keys'], rotation=45)
                plt.tight_layout()

                # Display the graph in the Streamlit app
                st.pyplot(fig)

                # Save the plot to a BytesIO object
                img_buffer = BytesIO()
                fig.savefig(img_buffer, format='png')
                img_buffer.seek(0)

                # Provide download button for the generated graph
                st.download_button(
                    label="Download Graph as PNG",
                    data=img_buffer,
                    file_name="generated_graph.png",
                    mime="image/png"
                )

    st.markdown('</div>', unsafe_allow_html=True)
