import streamlit as st
from langchain_openai import ChatOpenAI


def get_llm(family='gpt',model='gpt-3.5-turbo-0125',temperature=0.2):
    if family =='gpt':
        llm = ChatOpenAI(model=model, temperature=temperature)
        return llm
    else:
        return ChatOpenAI(model='gpt-3.5-turbo-0125', temperature=0.2)
    
def generate_text(system_prompt:str, human_prompt, temp=0.2):
    if type(human_prompt)== str:
        messages = [
            {"role": "system", "content": system_prompt },
            {"role": "human", "content": human_prompt }
    ]
        llm = get_llm(temperature=temp)
        output = llm.invoke(messages).content
        return output
    elif type(human_prompt)== list:
        messages = [
            {"role": "system", "content": system_prompt }]
        messages += human_prompt
        llm = get_llm(temperature=temp)
        output = llm.invoke(messages).content
        return output
    


st.title("Draft refinement")
TASK = st.text_input("TASK", placeholder="Mention the task.")

BG_INFO = st.text_area("BACKGROUND INFO ON PRODUCT", value="", placeholder='Add relevant info regarding the product')

ADDN_REQ = st.text_area("Additional requirements (optional)", value="", placeholder="Eg: Some sort of company regulations for social media, disclaimers etc")

PLANNER_PROMPT = '''Given a content generation task create a list of requirements for that task. Each step must be an independent simple sentence. Be creative with your response.
For extremely complicated tasks the number of steps can be maximum 10 however for simple task the steps should be much lower. 
The steps should be only regarding the actual content structure and tone and not about the additional steps like research, proof reading, outlining etc.
'''
DELEGATOR_PROMPT = st.text_area("DELEGATOR PROMPT",
                                 value = '''Given a task create a qualitative persona for a large language model bot who will be most suited to perform the task. The output is a short bio about their passions and skills. Start with 'You are a..' '''                           ,
                                 placeholder= '''Given a task create a qualitative persona for a large language model bot who will be most suited to perform the task. The output is a short bio about their passions and skills. Start with 'You are a..'
''')

WORKER_PROMPT = '''You are an assistant with the following persona.
Persona:{persona}. 
Perform the TASK given by the user as the persona. 
Craft your responses on the basis of the following information.
<info>
{info}
</info>
DIRECTIVES: If the user added suggestions, imbibe them while writing the content and adjust accordingly. Do not address the user and do not include any header or footer with the TASK output.
User's REQUIREMENTS that must be followed above all:
{steps}
'''

CRITIC_PROMPT = st.text_area("CRITIC_PROMPT", 
value = '''You are an AI proof reader who is picky about details and obsessed about content quality.
You are given a list of requirements for a content generation task and the output corresponding to that task. Use the requirements as guidelines. 
Suggest improvements as a list. Suggest a maximum of 5 improvements. Be precise and consise. 
 Do not provide anything else.
''')

#CUSTOM_CRITIC_PROMPT = st.text_area("CUSTOM CRITIC PROMPT", value="")
NUM_REFINEMENTS = st.number_input('Number of refinement cycles', value=2, step=1)
CRITIC_PROMPT =CRITIC_PROMPT + """
{task}
{steps}"""


if st.button("GO"):
    if TASK != "":
        iters = NUM_REFINEMENTS
        messages =[]
        messages.append({'role': 'human', 'content': TASK})
        with st.container(border= True):
            persona = generate_text(DELEGATOR_PROMPT, TASK, temp=0.5)
            st.write('PERSONA: \n', persona, '\n\n')
            steps = generate_text(PLANNER_PROMPT, TASK,temp=0.5)
            steps = steps + "\n\n\n ADDITIONAL REQUIREMENTS by user:\n\n " + ADDN_REQ
            st.write('STEPS: \n', steps)

        with st.expander("Content refinement"):   
            draft = generate_text(WORKER_PROMPT.format(persona=persona, info=BG_INFO, steps=ADDN_REQ), messages, temp=0.5)
            messages.append({'role': 'assistant', 'content': draft})
            st.markdown('#### DRAFT:')
            st.write(draft)
            for i in range(iters):
                #st.write('MESSAGES: ', messages)
                critic = generate_text(CRITIC_PROMPT.format(task = TASK, steps=steps), draft, temp=0.2)
                messages.append({'role': 'human', 'content': critic})
                st.markdown('#### CRITIQUE')
                st.write(critic)
                draft = generate_text(WORKER_PROMPT.format(persona=persona, info=BG_INFO, steps=steps), messages[-2:], temp=0.2)
                messages.append({'role': 'assistant', 'content': draft})
                st.markdown('#### DRAFT:')
                st.write(draft)
                


        st.markdown('#### Output')
        st.write(messages[-1]['content'])
    else:
        st.error("No task provided.")








