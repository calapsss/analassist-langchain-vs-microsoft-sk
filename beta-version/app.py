import streamlit as st
import pandas as pd
import numpy as np
import openai 

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    OpenAITextCompletion
)
from semantic_kernel.orchestration.context_variables import ContextVariables






# Define Streamlit app
def app():
    
    # Initialize Semantic Kernel
    kernel = sk.Kernel()
    api_key, org_id = sk.openai_settings_from_dot_env()
    kernel.add_text_completion_service(
            "dv", OpenAITextCompletion("gpt-3.5-turbo-instruct", api_key, org_id)
        )
    
    skills_directory = "semantic-kernel/skills"


    # Import skills
    interpret_skill = kernel.import_semantic_skill_from_directory(
        skills_directory, "Interpret"
    )

    analyzeDataframe_function = interpret_skill["AnalyzeDataframe"]
    decipherPrompt_function = interpret_skill["DecipherPrompt"]
    createQuery_function = interpret_skill["CreateQuery"]





    def ui_elements():
        #Variables
        df_analyzed = False

        #Stuff on Sidebar
        st.sidebar.header('Data Upload')
        st.sidebar.write('Upload your data here')
        uploaded_file = st.sidebar.file_uploader("Choose a file")

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file, header=1)

            df_analysis = analyzeDataframe_function(variables=ContextVariables(content=df.to_string()[:4000]))
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
            print(df_analysis)
            context_variables = ContextVariables(content=prompt, variables={"dataframe": df_analysis.translate()})
            result = decipherPrompt_function(variables=context_variables)
            print(result)
            st.write(result)

    ui_elements()






    
        


# Run Streamlit app
if __name__ == "__main__":
    app()






    

