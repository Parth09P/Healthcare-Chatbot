def validate_response(message: str) -> bool:
    """
    Validates the message to ensure it's related to health, and filters inappropriate content.
    :param message: String (user's input)
    :return: Boolean (True if valid, False if inappropriate)
    """
    health_keywords = ['health', 'medicine', 'doctor', 'treatment', 'appointment', 'diet', 'lifestyle']
    inappropriate_keywords = ['politics', 'religion', 'controversy', 'sensitive']

    # Check if the message is health-related
    if any(word in message.lower() for word in health_keywords):
        return True

    # Check if the message contains inappropriate content
    if any(word in message.lower() for word in inappropriate_keywords):
        return False

    # If neither, consider it irrelevant
    return False

def format_response(response: str) -> str:
    """
    Formats the AI response for better presentation.
    :param response: String (AI's response)
    :return: Formatted response string
    """
    return response.strip()  # Basic formatting, can be extended for more complex needs
