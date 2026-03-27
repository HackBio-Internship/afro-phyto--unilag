import uuid
import random
from django.db import models
from django.contrib.auth.models import User

# Status choices for contribution review
STATUS_CHOICES = [
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

# Accession number generator
def generate_accession_number():
    while True:
        number = random.randint(0, 999999)
        accession = f"APH{number:06d}"
        if not Contributor.objects.filter(accession_number=accession).exists():
            return accession

# Contributor Model/Table
class Contributor(models.Model):
    accession_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        default=generate_accession_number,
        help_text="Submission accession number (not phytochemical accession)"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    common_name = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='contributors/', blank=True, null=True)
    plant_description = models.TextField(blank=True, null=True)
    csv_file = models.FileField(upload_to='uploads/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.accession_number}"

# Plant Model/Table
class Plant(models.Model):
    scientific_name = models.CharField(max_length=255)
    common_names = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    contributor = models.ForeignKey(Contributor, on_delete=models.SET_NULL, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    image = models.ImageField(upload_to='plant_images/', null=True, blank=True)

    def __str__(self):
        return self.scientific_name

# Phytochemical Model/Table
class Phytochemical(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='phytochemicals')
    
    compound_name = models.CharField(max_length=255)
    compound_class = models.CharField(max_length=255, blank=True)
    
    # Core structure
    smiles = models.TextField(blank=True)
    inchikey = models.CharField(max_length=50, blank=True)
    pubchem_cid = models.CharField(max_length=50, blank=True)
    
    # Drug likeness descriptors
    molecular_weight = models.FloatField(null=True, blank=True)
    logp = models.FloatField(null=True, blank=True)
    h_donors = models.IntegerField(null=True, blank=True)
    h_acceptors = models.IntegerField(null=True, blank=True)

    # Decision flag
    lipinski_pass = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.compound_name

# Scientific Literature Model/Table
class ScientificLiterature(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='literature')
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    journal = models.CharField(max_length=255)
    doi = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title

# Manual Phytochemical Entry Model/Table
class ContributorPhytochemical(models.Model):
    contribution = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name="manual_phytochemicals")
    compound_name = models.CharField(max_length=255)
    compound_class = models.CharField(max_length=255, blank=True)
    smiles = models.TextField(blank=True)

    def __str__(self):
        return self.compound_name  

# Manual Literature Entry Model/Table
class ContributorLiterature(models.Model):
    contribution = models.ForeignKey(
        Contributor,
        on_delete=models.CASCADE,
        related_name="manual_literature"
    )
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    journal = models.CharField(max_length=255)
    doi = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title

# Contact Message Model/Table
class ContactMessage(models.Model):
    fname = models.CharField(max_length=150)
    lname = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fname} {self.lname} - {self.subject}"

# Docking Job Model/Table
class DockingJob(models.Model):
    job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    job_name = models.CharField(max_length=200)
    email = models.EmailField()
    num_poses = models.IntegerField(default=20)
    steps = models.IntegerField(default=18)
    save_trajectory = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    results_json = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.job_name} ({self.job_id})"

# AuditTrail for Contributions
class ContributionAudit(models.Model):
    ACTION_CHOICES = [
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    contribution = models.ForeignKey(
        Contributor,
        on_delete=models.CASCADE,
        related_name="audits"
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.contribution.accession_number} - {self.action}"
