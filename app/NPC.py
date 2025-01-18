import openai
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NPC(Base):
    __tablename__ = "npcs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    location = Column(String)
    backstory = Column(Text)

    def __init__(
        self,
        name=None,
        description=None,
        location=None,
        api_key=None,
        backstory=None,
        generate_backstory=False,
    ):
        self.api_key = api_key
        self.name = name or self.generate_name_with_chatgpt(description)
        self.backstory = (
            backstory or self.generate_backstory_with_chatgpt(description)
            if generate_backstory
            else None
        )
        self.description = description
        self.location = location

    def generate_name_with_chatgpt(self, description):
        ## TODO: Ensure this doesn't get re-run too many times.
        """
        Generates a name for the NPC using ChatGPT API based on the provided description.
        """
        if not self.api_key:
            raise ValueError("API key is required to use ChatGPT for name generation.")

        prompt = (
            f"Create a unique and fitting name for an NPC based on the following description:\n\n"
            f"Description: {description if description else 'No description provided.'}"
        )
        try:
            openai.api_key = self.api_key
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative name generator.  Return only the name.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=50,
            )
            name = response.choices[0].message.content.strip()
            return name if name else "Unnamed NPC"
        except Exception as e:
            print(f"Error generating name with ChatGPT: {e}")
            return "Unnamed NPC"

    def generate_backstory_with_chatgpt(self, description):
        ## TODO: Ensure this doesn't use too many tokens and the response isn't too long.
        ## TODO: Ensure this doesn't get re-run too many times.
        if not self.api_key:
            raise ValueError(
                "API key is required to use ChatGPT for backstory generation."
            )

        prompt = (
            f"Create a unique and fitting backstory for an NPC based on the following description:\n\n"
            f"Description: {description if description else 'No description provided.'}"
        )
        try:
            openai.api_key = self.api_key
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative backstory generator.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            backstory = response.choices[0].message.content.strip()
            return backstory if backstory else "Unnamed NPC"
        except Exception as e:
            print(f"Error generating name with ChatGPT: {e}")
            return "Unnamed NPC"
