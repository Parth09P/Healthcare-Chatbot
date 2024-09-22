from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from .models import Patient
from .ai_models.factory import AIChatbotFactory  # Import the AI chatbot factory
from django.conf import settings  # To fetch the chatbot model and API key from settings
from django.utils.html import strip_tags
from .models import ConversationSummary 
import google.generativeai as genai

class ChatView(View):
    def get(self, request):
        # Fetch the first patient's data from the database
        patient = Patient.objects.first()

        # Check if chat history is not in session (indicating a new session or app restart)
        if 'chat_history' not in request.session:
            # Clear session chat history
            request.session['chat_history'] = []

            # Clear summaries from the database for this patient
            if patient:
                self.clear_chat_history_and_summaries(patient.id, request)

        # Prepare patient data for rendering
        patient_data = {
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'medical_condition': patient.medical_condition,
        } if patient else None

        # Render the chat page with the current chat history and patient data
        return render(request, 'chat.html', {
            'chat_history': request.session['chat_history'],
            'patient_data': patient_data  # Ensure this is correctly passed
        })

    def post(self, request):
        user_message = request.POST.get('message').strip()  # Get and strip the message to remove extra spaces
        if user_message:  # Only process if the message is not empty
            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

            # Append patient's message to the session's chat history
            chat_history = request.session.get('chat_history', [])
            chat_history.append({
                'sender': 'Patient',
                'message': user_message,
                'timestamp': timestamp
            })

            # Fetch the first patient's data from the database
            patient = Patient.objects.first()
            patient_info = self.prepare_patient_info(patient)

            # Initialize chatbot through the factory
            model_name = settings.CHATBOT_MODEL  # Get the model name from settings
            api_key = settings.CHATBOT_API_KEY  # Get the API key from settings
            chatbot = AIChatbotFactory.create_chatbot(model_name, api_key)  # Get the AI chatbot instance

            try:
                # Prepare chat history string
                history_string = "\n".join([f"{entry['sender']}: {entry['message']}" for entry in chat_history])

                system_prompt = (
                    "You are a health assistant bot. Your primary function is to respond to inquiries "
                    "related to health and medical topics. You should address questions about: \n"
                    "- General health and lifestyle inquiries (e.g., exercise, nutrition, mental health).\n"
                    "- The patient's medical condition, medication regimen, and dietary advice.\n"
                    "- Requests from the patient to their doctor, such as medication changes or appointment scheduling.\n"
                    "Do not respond to unrelated, sensitive, or controversial topics. These include but are not limited to:\n"
                    "- Political issues\n"
                    "- Personal opinions\n"
                    "- Discussions about mental health without a clear health context\n"
                    "- Anything that could be considered offensive or inappropriate.\n"
                    "If a patient asks for assistance outside of these topics, kindly inform them "
                    "that you can only assist with health-related inquiries."
                    f"Here's the patient's info: {patient_info}"
                )

                user_prompt = f"{user_message}"  # Replace user_message with the actual input

                bot_prompt = f"{system_prompt}\nChat history:\n{history_string}\nPatient: {user_prompt}\n AI:"

                # Generate bot's response with chat history included
                # bot_prompt = (
                #     f"You are a professional health assistant. {patient.first_name} is a patient. He says: {user_message}.\n"
                #     f"Chat history:\n{history_string}\n"
                #     "Respond to the patient directly as if you're talking to him. No need to address them by his their everytime."
                # ) if patient else f"You said: {user_message}\nChat history:\n{history_string}"

                bot_response = chatbot.generate_response(bot_prompt)

                # Append bot's response to the chat history
                chat_history.append({
                    'sender': 'AI Bot',
                    'message': bot_response,
                    'timestamp': timestamp
                })

                # Store the chat history in session until 10 messages, then summarize
                if len(chat_history) >= 10:  # Adjusted to 10 messages for summarization
                    # Fetch last 10 messages
                    messages_to_summarize = " ".join([entry['message'] for entry in chat_history[-10:]])

                    # Summarize conversation using LLM
                    summary = self.summarize_conversation(messages_to_summarize)

                    # Store the summary in the database
                    self.store_summary_in_db(patient.id, summary)

                    # Clear the session chat history after summarization
                    request.session['chat_history'] = []

            except Exception as e:
                bot_response = f"Error: {str(e)}"

            # Update the session chat history
            request.session['chat_history'] = chat_history

        # Redirect to the same page (PRG pattern)
        return redirect('chat')  # 'chat' is the name of your URL
    
    def prepare_patient_info(self, patient):
        patient_info = (
            f"Patient Name: {patient.first_name} {patient.last_name}\n"
            f"Date of Birth: {patient.date_of_birth}\n"
            f"Phone Number: {patient.phone_number}\n"
            f"Email: {patient.email}\n"
            f"Medical Condition: {patient.medical_condition}\n"
            f"Medication Regimen: {patient.medication_regimen}\n"
            f"Last Appointment: {patient.last_appointment}\n"
            f"Next Appointment: {patient.next_appointment}\n"
            f"Doctor's Name: {patient.doctor_name}"
        )
        return patient_info

    # Function to call the LLM and summarize the last 10 messages
    def summarize_conversation(self, conversation_text):
        """
        Use the Gemini API to generate a response to the input message.
        """
        try:
            # Replace this with the actual API call to Gemini
            # Assuming Gemini has an endpoint like '/generate' or '/chat'
            genai.configure(api_key=settings.CHATBOT_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            # print(message)
            response = model.generate_content(f"Summarize the following conversation: {conversation_text}")

            # Extract the relevant text from the Gemini API response
            return response.text

        except Exception as e:
            return f"Error in generating response from Gemini: {str(e)}"

    # Function to store the summary in the PostgreSQL database
    def store_summary_in_db(self, patient_id, summary):
        # Store or update the summary in the database
        ConversationSummary.objects.create(
            patient_id=patient_id,
            summary=summary
        )

    # Function to clear session and delete summaries
    def clear_chat_history_and_summaries(self, patient_id, request):
        # Clear session chat history
        request.session['chat_history'] = []

        # Delete summaries for this patient
        ConversationSummary.objects.filter(patient_id=patient_id).delete()