import requests

from .base import AIChatbot
import google.generativeai as genai
import os

class GeminiChatbot(AIChatbot):
    """
    AI Chatbot using the Gemini API.
    """
    def __init__(self, api_key: str):
        """
        Initialize the Gemini API with the provided API key.
        """
        self.api_key = api_key
        
        
        # Set up any other configurations if required by the Gemini API

    def generate_response(self, message: str) -> str:
        """
        Use the Gemini API to generate a response to the input message.
        """
        try:
            # Replace this with the actual API call to Gemini
            # Assuming Gemini has an endpoint like '/generate' or '/chat'
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            # print(message)
            response = model.generate_content(message)

            # Extract the relevant text from the Gemini API response
            return response.text

        except Exception as e:
            return f"Error in generating response from Gemini: {str(e)}"