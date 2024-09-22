from abc import ABC, abstractmethod

class AIChatbot(ABC):
    """
    Abstract base class that defines the structure of an AI chatbot.
    Any AI model integrated into the app must implement these methods.
    """

    @abstractmethod
    def generate_response(self, message: str) -> str:
        """
        Takes a user message as input and returns the AI-generated response as output.
        """
        pass