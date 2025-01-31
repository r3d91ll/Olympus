from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

class TagGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=["user_query"],
            template=(
                "Generate descriptive tags for the following queries. Focus on user "
                "intention, relevant entities, and keywords. Extend these tags to related, "
                "unmentioned terms that are contextually relevant.\n\n"
                "Guidelines:\n"
                "Topic: Identify user intention or subject area the query pertains to.\n"
                "Entity Recognition: Focus on recognizable entities common in similar queries.\n"
                "Keywords: Extract specific terms or verbs that define the query's intent.\n"
                "Related Tags: Include tags that are related to user intention, even if not "
                "directly mentioned, to provide broader contextual understanding.\n\n"
                "Query: {user_query}\n"
                "Tags:\n"
            )
        )

    def generate_tags(self, user_query):
        chain = RunnableSequence(
            first=self.prompt_template,
            last=self.llm
        )
        response = chain.invoke({"user_query": user_query})
        tags = [tag.strip() for tag in response.split(',') if tag.strip()]
        return tags
