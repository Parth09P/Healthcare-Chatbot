import google.generativeai as genai
from django.conf import settings
from .base import AIChatbot

class GeminiChatbot(AIChatbot):
    """
    AI Chatbot using the Gemini API.
    """
    def __init__(self, api_key: str):
        """
        Initialize the Gemini API with the provided API key.
        """
        self.api_key = api_key
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        # genai.configure(api_key=self.api_key)

    def generate_response(self, message: str) -> str:
        """
        Use the Gemini API to generate a response to the input message.
        """
        try:
            genai.configure(api_key=self.api_key)
            response = self.model.generate_content(message)
            return response.text

        except Exception as e:
            return f"Error in generating response from Gemini: {str(e)}"
    
    def extract_entities(self, user_message):
        # Call the Gemini API to extract entities
        """
        Use the Gemini API to generate a response to the input message.
        """
        try:
            genai.configure(api_key=self.api_key)
            response = self.model.generate_content(f"Get entities from the following user message: {user_message}.\nMake sure that you return the entities in a JSON response. Return only the valid JSON response.")
            return response.text

        except Exception as e:
            return f"Error in generating response from Gemini: {str(e)}"

    # Function to call the LLM and summarize the last 10 messages
    def summarize_conversation(self, user_message):
        """
        Use the Gemini API to generate a response to the input message.
        """
        try:
            genai.configure(api_key=self.api_key)
            response = self.model.generate_content(f"Summarize the following conversation: {user_message}")
            return response.text

        except Exception as e:
            return f"Error in generating response from Gemini: {str(e)}"