from .openai_model import OpenAIChatbot
from .gemini_model import GeminiChatbot
# Import other chatbot models if needed, such as Gemini, etc.

class AIChatbotFactory:
    """
    Factory to create instances of different AI chatbot models.
    """

    @staticmethod
    def create_chatbot(model_name: str, api_key: str):
        """
        Creates an instance of a chatbot based on the model_name.

        :param model_name: Name of the AI model to use (e.g., 'openai', 'gemini').
        :param api_key: API key for the model.
        :return: Instance of a chatbot.
        """
        if model_name.lower() == 'openai':
            return OpenAIChatbot(api_key=api_key)
        
        # Future chatbot models like Gemini can be added here:
        elif model_name.lower() == 'gemini':
            return GeminiChatbot(api_key=api_key)
        
        else:
            raise ValueError(f"Unknown AI model: {model_name}")
