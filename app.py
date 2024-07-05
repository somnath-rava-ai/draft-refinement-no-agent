import dspy
import streamlit as st
from typing import List
from io import StringIO


#st.title("Sale_transcript_downstream_ops")
st.header('Sales transcript :scroll: -> Content outlines :memo:', divider='violet')

gpt3_turbo = dspy.OpenAI(model='gpt-3.5-turbo-0125', max_tokens=2000, temperature=0.2)
dspy.configure(lm=gpt3_turbo)

class Parse(dspy.Signature):
    """Accept a sales call transcript and generate the relevant outputs"""
    transcript:str = dspy.InputField(desc="Transcript of a sales call between a product seller and a prospective buyer.")
    summary:str = dspy.OutputField(desc="Rigorously detailedmeeting-minutes by going though the call transcript in a point-wize list.")
    product:str = dspy.OutputField(desc="Name of the specific product being pitched and  its selling point to the client as mentioned in the transcript.")
    industry:str = dspy.OutputField(desc="Name of Industry of the prospective client's firm.")
    faq:str = dspy.OutputField(desc= "FAQ questions derived from the transcript conversation a that are useful to know and should be added to a FAQ collection, regarding usage, security, product updates etc. The FAQ questions must not address any client directly")
    
class Ideas(dspy.Signature):
    """Generate content ideas keeping in mind the mentioned content_type by going through the summary of a call transcript and brainstorm a list of distinctive ideas brought up within that sales transcript that could be transformed into an interesting and engaging educational content or followup communication media. Focus on concepts at the intersection of the product or service of the seller and the prospect's industry. """
    content_type:str = dspy.InputField(desc="This is the final form of the content what will be published.")
    summary:str = dspy.InputField(desc=" minutes of meeting from the transcript")
    product:str = dspy.InputField(desc="Name of the specific product being pitched. Also utlities and use cases mentioned in the transcript")
    industry:str = dspy.InputField(desc="Industry of the prospective client")
    ideas:str = dspy.OutputField(desc="""list of generic content ideas in line with content_type""")
    

class SelectedIdea(dspy.Signature):
    """discern the most interesting and distinctive content idea that the seller would want to run from the list of ideas on the basis of relevance to the prospect's industry. """
    ideas:str = dspy.InputField(desc="list of concepts titles")
    industry:str = dspy.InputField(desc="Industry of the prospective client")
    content_type:str = dspy.InputField(desc="Type of content that the user wants.")
    best_idea:str = dspy.OutputField(desc= "the best concept title from ideas. nothing else")
    reason:str = dspy.OutputField(desc= "provide a reasoning why this is good content for the seller to put out there, whether it's because it frames their product positively or it simply offers helpful education to readers")
    
class TitleAndOutlines(dspy.Signature):
    """take the idea and product information and create title and content outlines for the given content_type."""
    idea:str = dspy.InputField(desc="concepts title")
    product:str = dspy.InputField(desc="Product description of seller")
    content_type:str = dspy.InputField(desc="Type of content that the user wants.")
    titleandoutlines:str  = dspy.OutputField(desc="Output format:Title followed by a list of outlines")

class SalesCallProcess(dspy.Module):
    def __init__(self):
        super().__init__()
        self.parse = dspy.Predict(Parse)
        self.ideas = dspy.ChainOfThought(Ideas)
        self.content_selection = dspy.ChainOfThought(SelectedIdea)
        self.title_and_outlines = dspy.ChainOfThought(TitleAndOutlines)
    def forward(self, input_transcript:str, content_type:str):
        parse_output = self.parse(transcript=input_transcript)
        ideas_output = self.ideas(summary=parse_output.summary, product=parse_output.product, industry=parse_output.industry, content_type=content_type)
        content_selection_output = self.content_selection(ideas=ideas_output.ideas, industry=str(parse_output.industry), content_type=content)
        title_and_outlines_output = self.title_and_outlines(idea=content_selection_output.best_idea, product=parse_output.product, content_type=content)
        
        return parse_output.summary, parse_output.product, parse_output.industry, parse_output.faq, ideas_output.ideas, content_selection_output.best_idea, content_selection_output.reason, title_and_outlines_output.titleandoutlines
    

    
text = """

Amit: Hello Bhavesh, I’m Amit, a marketing manager at Rava.ai. How’s your day going?

Bhavesh: It’s going fine, Amit. What can I do for you?

Amit: I’d like to share some information about Rava.ai, an AI-powered marketing platform designed for startups like ACME Corp. Have you heard of AI tools for marketing before?

Bhavesh: Not really, I’m quite skeptical about new tools. We’re doing fine with our current marketing strategies.

Amit: I understand your concerns, Bhavesh. Rava.ai aims to streamline marketing efforts, drive growth, and help businesses stay ahead of the competition. It offers a full-stack marketing platform with features like Plan, Train, and Create.

Bhavesh: Plan, Train, and Create? What do those mean?

Amit: Plan analyzes your business and market to create personalized marketing plans. Train acts as a central knowledge hub, storing crucial information about your brand and guiding you to understand your customers. Create streamlines the content creation process, offering tools for marketing assets like emails, blog posts, and social media posts.

Bhavesh: Sounds interesting, but how would it benefit us?

Amit: Rava AI helps increase efficiency by reducing marketing waste and maximizing budget, drives real results with boosted conversions, sales, and revenue, and keeps you ahead of the competition with AI-powered insights. It allows you to focus on high-leverage activities.

Bhavesh: I see, but we’re doing well without any AI tools. Why should we consider Rava.ai?

Amit: Rava.ai helps businesses scale, stay agile, and make data-driven decisions to drive sustainable growth. It’s currently in the MVP stage and undergoing testing to achieve product-market fit.

Bhavesh: MVP, you mean it’s not fully developed yet?

Amit: That’s correct, but we’re confident in its potential and would love for ACME Corp to be part of our testing and feedback process.

Bhavesh: I appreciate the offer, Amit, but I think we’ll stick with our current strategies for now.

Amit: I completely understand, Bhavesh. If you have any questions or change your mind in the future, please don’t hesitate to reach out. Thanks for your time today.

Bhavesh: You’re welcome, Amit. Have a great day.

Amit: You too, Bhavesh. Goodbye.

Bhavesh: Goodbye.

(30 dialogues)
"""

inputted_transcript = st.text_area("Transcript", placeholder="Paste your transcript here", height=300)

content = st.text_input("Content", placeholder="What type of content do you want")
if st.button("Process"):
    sales_call_process = SalesCallProcess()
    summary, product, industry, faq, ideas, best_idea, reason, titleandoutlines= sales_call_process(input_transcript=inputted_transcript, content_type=content)

    with st.expander("Ideas"):
        st.markdown("## Summary")
        st.markdown(f"{summary}")
        st.markdown("## Product")
        st.markdown(f"{product}")
        st.markdown("## Target Industry")
        st.markdown(f"{industry}")
        st.markdown(f"## Ideas:")
        st.markdown(f"{ideas}")
    st.markdown("## Best idea:")
    st.markdown(f"{best_idea}")
    st.markdown("## Justification:")
    st.markdown(f"{reason}")
    st.markdown("## Title and Outlines:")
    st.markdown(f"{titleandoutlines}")
    st.markdown("## FAQ:")
    st.markdown(f"{faq}")




