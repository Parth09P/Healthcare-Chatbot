from django.db import models
from django.utils import timezone

class Patient(models.Model):
    first_name = models.CharField(max_length=100, db_column='first_name')
    last_name = models.CharField(max_length=100, db_column='last_name')
    date_of_birth = models.DateField(db_column='date_of_birth')
    phone_number = models.CharField(max_length=15, db_column='phone_number')
    email = models.EmailField(db_column='email')
    medical_condition = models.TextField(db_column='medical_condition')
    medication_regimen = models.TextField(db_column='medication_regimen')
    last_appointment = models.DateTimeField(db_column='last_appointment')
    next_appointment = models.DateTimeField(db_column='next_appointment')
    doctor_name = models.CharField(max_length=100, db_column='doctor_name')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'patients'

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