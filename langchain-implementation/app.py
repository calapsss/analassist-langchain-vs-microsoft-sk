import streamlit as st
import pandas as pd
import numpy as np
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
import re
import os

chat_model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-3.5-turbo")

class semanticFunctions:
    #Analyze Dataframe
    analyzeDfSystemTemplate = "You are tasked with analyzing a dataset."
    analyzeDfTemplate = """
        YOU ARE GIVEN A DATAFRAME. 
        DESCRIBE THE DATAFRAME.
        GIVE A BRIEF SUMMARY OF THE DATAFRAME.
        LIST THE NECESSARY COLUMNS.
        ---------------------------
        {dataframe}
     """
    
    analyzeDfPrompt = ChatPromptTemplate.from_messages([
        ("system",analyzeDfSystemTemplate),
        ("human", analyzeDfTemplate),
    ]
    )
    analyzeDfChain = analyzeDfPrompt | chat_model | StrOutputParser()

    #Decipher Prompt
    decipherPromptSystem = "You are a prompt engineer"
    decipherPromptTemplate = """
        MODIFY THE ORIGINAL PROMPT TO MAKE IT INTERPRETABLE BY THE OTHER LLM.

        CONTEXT: 
        YOU ARE A PROMPT ENGINEER AND YOUR PROMPT WILL BE USED FOR THE OTHER LLM.
        YOU ARE GIVEN A PROMPT AND A DATAFRAME.
        THE OTHER LLM GENERATES CODE FOR A PANDAS DATAFRAME BASED ON THE PROMPT.

        DO NOT OUTPUT THE CODE. OUTPUT THE MODIFIED PROMPT.

        +++++
        DATAFRAME INFORMATION:
        {dataframe}
        +++++
        ORIGINAL PROMPT:
        {input}
        +++++
    """

    decipherPrompt = ChatPromptTemplate.from_messages([
        ("system", decipherPromptSystem),
        ("human", decipherPromptTemplate),
    ])
    decipherPromptChain = decipherPrompt | chat_model | StrOutputParser()


    #GenerateCode
    generateCodeSystem = "You are a code generator"
    generateCodeTemplate = """
        GENERATE A CODE FOR PANDAS DATAFRAME TO ACHIEVE THE TASK. 

        DO NOT DEFINE THE DATAFRAME AGAIN
        +++++
        DO NOT IMPORT LIBRARIES AGAIN
        +++++
        ONLY USE STREAMLIT FOR GRAPHS AND CHARTS
        +++++
        ASSUME THAT dataframe is already defined as df
        ASSUME THAT  user should be able to view the output on streamlit
        ASSUME THAT the following Libraries are already imported:
        1. pandas as pd
        2. streamlit as st 
        +++++
        MARK THE START AND END OF THE CODE WITH '[STARTCODE]' AND '[ENDCODE]'
        +++++
        IF YOU HAVE VISUALIZATIONS USE Chart Elements from streamlit.
        WRITE EXPLANATION OF THE DATAFRAME AND RELATE IT TO THE TASK. 
        +++++
        TASK:
        {input}
        +++++
        DATAFRAME INFO:
        {dataframe}
        +++++

        [STARTCODE]
        (Enter Your Here)
        [ENDCODE]

        [EXPLANATION]
        (Your Explanation)
        [ENDEXPLANATION]
    """
    generateCodePrompt = ChatPromptTemplate.from_messages([
        ("system", generateCodeSystem),
        ("human", generateCodeTemplate),
    ])
    generateCodeChain = generateCodePrompt | chat_model | StrOutputParser()

    # Code Repair
    repairCodeSystem = "You are a code repairer"
    repairCodeTemplate = """
        PROVIDE A NEW CODE GIVEN THE TASK AND DATAFRAME TO FIX THE ERROR FROM PREVIOUS CODE.

        +++++
        TASK:
        {{$task}}
        +++++
        DATAFRAME INFO:
        [START DF]
        {{$df}}
        [END DF]
        +++++
        PREVIOUS CODE:
        [START CODE]
        {{$code}}
        [END CODE]
        +++++
        ERROR:
        [ERROR]
        {{$input}}
        [END ERROR]
        +++++
        [NEWCODE]
        Add Your Code Here
        [ENDNEWCODE]
    """

    repairCodePrompt = ChatPromptTemplate.from_messages([
        ("system", repairCodeSystem),
        ("human", repairCodeTemplate),
    ])

    repairCodeChain = repairCodePrompt | chat_model | StrOutputParser()




def app():

    


    def ui_elements():
        #Variables
        df_analyzed = False

        #Stuff on Sidebar
        st.sidebar.header('Data Upload')
        st.sidebar.write('Upload your data here')
        uploaded_file = st.sidebar.file_uploader("Choose a file")

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            analydf = df.head().to_string()
            print(analydf)
            try:
                analydf = semanticFunctions.analyzeDfChain.invoke({"dataframe": analydf})
                df_analyzed = True
            except:
                df_analyzed = False
                st.sidebar.write('Error analyzing dataframe')
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
            try:
                if df_analyzed:
                    message = semanticFunctions.decipherPromptChain.invoke({"dataframe": analydf, "input": message})
                    response = semanticFunctions.generateCodeChain.invoke({"dataframe": analydf, "input": message})
                    try:
                        code = re.search(r'\[STARTCODE\]\n(.*?)\n\[ENDCODE\]', response, re.DOTALL).group(1)
                    except:
                        code = 'st.write("Error")'
                    try:
                        explanation = re.search(r'\[EXPLANATION\]\n(.*?)\n\[ENDEXPLANATION\]', response, re.DOTALL).group(1)
                    except:
                        explanation = "No Explanation"
                    
                    #Try to execute code 3 times and if error use CodeRepair Chain
                    error_message = ""
                    x = 0
                    while x < 3:
                        try:
                            exec(code)
                            break
                        except:
                            error_message = "Error Executing Code Trying repair code"
                            response = semanticFunctions.repairCodeChain.invoke({"dataframe": analydf, "input": error_message, "code": code, "task": message})
                            code = re.search(r'\[NEWCODE\]\n(.*?)\n\[ENDNEWCODE\]', response, re.DOTALL).group(1)
                            x += 1
                    st.write(explanation)
                else:
                    st.write("Please upload a dataframe first")
            except:
                st.write("Error processing message")


       


    ui_elements()


if __name__ == "__main__":
    app()
