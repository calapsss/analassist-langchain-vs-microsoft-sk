import streamlit as st
import pandas as pd
import numpy as np
import openai 
import re
import numpy as np
import matplotlib.pyplot as plt
import semantic_kernel as sk
import traceback
from semantic_kernel.connectors.ai.open_ai import (
    OpenAITextCompletion,
    OpenAIChatCompletion,
)
from semantic_kernel.orchestration.context_variables import ContextVariables





# Define Streamlit app
def app():
    
    # Initialize Semantic Kernel
    kernel = sk.Kernel()
    api_key, org_id = sk.openai_settings_from_dot_env()
    kernel.add_chat_service(
            "chat_completion", 
            OpenAIChatCompletion("gpt-3.5-turbo", api_key, org_id)
        )
    
    skills_directory = "semantic-kernel/plugins"


    # Import skills
    interpret_skill = kernel.import_semantic_skill_from_directory(
        skills_directory, "Interpret"
    )
    codegen_skill = kernel.import_semantic_skill_from_directory(
        skills_directory, "CodeGen"
    )

    analyzeDataframe_function = interpret_skill["AnalyzeDataframe"]
    decipherPrompt_function = interpret_skill["DecipherPrompt"]
    createQuery_function = codegen_skill["GenerateCode"]
    repairCode_function = codegen_skill["CodeRepair"]


    def ui_elements():
        #Variables
        df_analyzed = False

        #Stuff on Sidebar
        st.sidebar.header('Data Upload')
        st.sidebar.write('Upload your data here')
        uploaded_file = st.sidebar.file_uploader("Choose a file")

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            analydf = df.head()
            print("Doing Dataframe Analysis... \n\n")
            print("PROMPT: ", analydf)
            df_analysis = analyzeDataframe_function(variables=ContextVariables(content=analydf.to_string()[:4000])).result
            print("RESPONSE: ", df_analysis)
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
        if submit_button and uploaded_file is not None:
            prompt = f"{message}"
            print("INTERPRETING PROMPT...")
            print("Prompt: ", prompt)
            context_variables = ContextVariables(content=prompt, variables={"dataframe": df_analysis})
            modifiedPrompt = decipherPrompt_function(variables=context_variables).result
            print("Response: ", modifiedPrompt)
            print("GENERATING CODE... \n\n")
            print("Prompt: ", modifiedPrompt)
            context_variables = ContextVariables(content=modifiedPrompt, variables={"dataframe": df_analysis})
            responseTask = createQuery_function(variables=context_variables).result
            print("RESPONSE: ", responseTask)
            try:
                code = re.search(r'\[STARTCODE\]\n(.*?)\n\[ENDCODE\]', responseTask, re.DOTALL).group(1)
            except:
                code = 'st.write("Error")'
            
            try:
                explanation = re.search(r'\[EXPLANATION\]\n(.*?)\n\[ENDEXPLANATION\]', responseTask, re.DOTALL).group(1)
            except:
                explanation = "No Explanation"
            

            error_message = ""
            x=0
            while x < 3:
                try:
                    exec(code)
                    x = 4
                except Exception as e:
                    if (x == 2):
                        st.write("Error: ", e)
                    x += 1
                    error_message = traceback.format_exc()
                    print("Trying to repair code...")
                    context_variables = ContextVariables(content=error_message, 
                                                         variables={"task": modifiedPrompt, 
                                                                    "df": df_analysis, 
                                                                    "code": code, })
                    print("Prompt: ", error_message)
                    code  = repairCode_function(variables=context_variables).result
                    print("Response: ", code)
                    




            
            st.write(explanation)

    ui_elements()


# Run Streamlit app
if __name__ == "__main__":
    app()






    

