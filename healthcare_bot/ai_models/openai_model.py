import openai
from .base import AIChatbot
from openai import OpenAI

class OpenAIChatbot(AIChatbot):
    """
    AI Chatbot using OpenAI's GPT model.
    """

    def __init__(self, api_key: str):
        """
        Initialize the OpenAI API with the provided API key.
        """
        self.api_key = api_key
        openai.api_key = self.api_key

    def generate_response(self, message: str) -> str:
        """
        Use OpenAI's GPT model to generate a response to the input message.
        :param message: The user's message.
        :return: AI's response as a string.
        """
        try:
            print(f'Message:{message}')
            client = OpenAI(api_key=openai.api_key)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": message}
                ]
            )
            # response = openai.Completion.create(
            #     engine="text-davinci-003",  # Or switch to "gpt-4" if available.
            #     prompt=message,
            #     max_tokens=150,  # Limit response length.
            #     n=1,  # We want only a single response.
            #     stop=None,  # No special stopping conditions needed.
            #     temperature=0.7  # Controls randomness/creativity.
            # )
            # Return the cleaned response text
            return completion.choices[0].text.strip()
        
        
        
        except Exception as e:
            # Catch-all for other exceptions
            return f"Error in generating response: {str(e)}"