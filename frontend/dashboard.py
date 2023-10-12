import streamlit as st
import pandas as pd
import numpy as np
import openai 


openai.api_key = "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"

def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
               "role": "system", 
               "content": "You are a data analyst."
            },
            {
                "role":"user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content






# Define Streamlit app
def app():
    #Stuff on Sidebar
    st.sidebar.header('Data Upload')
    st.sidebar.write('Upload your data here')
    uploaded_file = st.sidebar.file_uploader("Choose a file")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.sidebar.write('Data uploaded successfully')


    #Main page
    st.title('📊 AnalAssist')
    st.write('Your personal assistant for data analysis. Chat with your data and create visualizations with ease. Ask AnalAssist questions about your data and get answers in seconds.')

    #Button on click to check data
    if st.button('Check Data') and uploaded_file is not None:
        st.write(df.head())
        if st.button('Exit'):
            st.stop()

    # Create form to submit messages bring to bottom of page
    
    form = st.form(key="chat_form")
    message = form.text_input(label="Message")
    submit_button = form.form_submit_button(label="Send")

   

    # Generate response when submit button is clicked
    if submit_button:
        prompt = f"User: {message}\nAnalAssist:"
        response = generate_response(prompt)
        st.write(response)


    
        


# Run Streamlit app
if __name__ == "__main__":
    app()






    

