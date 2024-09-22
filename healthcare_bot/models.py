from django.db import models
from django.utils import timezone

# Create your models here.
class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    medical_condition = models.CharField(max_length=255)
    medication_regimen = models.TextField()
    last_appointment = models.DateTimeField()
    next_appointment = models.DateTimeField()
    doctor_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ChatMessage(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    sender = models.CharField(max_length=50)  # 'Patient' or 'AI Bot'
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message} at {self.timestamp}"
    
class ConversationSummary(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)  # Link to the Patient model
    summary = models.TextField()  # Stores the summarized conversation
    last_updated = models.DateTimeField(default=timezone.now)  # Timestamp for when this summary was created/updated

    def __str__(self):
        return f"Summary for {self.patient.first_name} (Last Updated: {self.last_updated})"