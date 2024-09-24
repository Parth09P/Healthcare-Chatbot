from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from django.conf import settings  

from .models import Patient, ConversationSummary 
from .ai_models.factory import AIChatbotFactory  

# Index View
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')

# Chat View
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
            'doctor_name': patient.doctor_name,
        } if patient else None

        # Render the chat page with the current chat history and patient data
        return render(request, 'chat.html', {
            'chat_history': request.session['chat_history'],
            'patient_data': patient_data 
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

            # Initialize response variables
            response_message = ""
            review_message = ""

            # Check for appointment rescheduling request
            if "reschedule" in user_message.lower():
                # Example extraction of requested time
                response_message = f"I will convey your request to {patient.doctor_name}."
                review_message = f"Patient {patient.first_name} is requesting his appointment on {patient.next_appointment} to be changed."
                print(review_message)
                # Append bot's response to the chat history
                chat_history.append({
                    'sender': 'AI Bot',
                    'message': response_message,
                    'timestamp': timestamp
                })
            else:

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

                    user_prompt = f"{user_message}"  
                    bot_prompt = f"{system_prompt}\nChat history:\n{history_string}\nPatient: {user_prompt}\n AI:"
                    bot_response = chatbot.generate_response(bot_prompt)

                    # Append bot's response to the chat history
                    chat_history.append({
                        'sender': 'AI Bot',
                        'message': bot_response,
                        'timestamp': timestamp
                    })

                    # Call LLM for entity extraction
                    entities = chatbot.extract_entities(user_message)

                    print(f'Entities: {entities}')

                    # Check if the number of messages is a multiple of 10
                    if len(chat_history) % 10 == 0 and len(chat_history) > 0:  # Only trigger if there are 10 or more messages
                        # Fetch last 10 messages
                        messages_to_summarize = " ".join([entry['message'] for entry in chat_history[-10:]])

                        # Summarize conversation using LLM
                        summary = chatbot.summarize_conversation(messages_to_summarize)
                        print(f'Summary: {summary}')

                        # Store the summary in the database and clear the session
                        self.store_summary_in_db(patient.id, summary)
                        request.session['chat_history'] = []
                    else:
                        # Update the session chat history
                        request.session['chat_history'] = chat_history

                except Exception as e:
                    bot_response = f"Error: {str(e)}"

                # Update the session chat history
            request.session['chat_history'] = chat_history

        # Redirect to the same page (PRG pattern)
        return redirect('chat') 
    
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
        # ConversationSummary.objects.filter(patient_id=patient_id).delete()