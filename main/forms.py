from django import forms
from .models import Contributor, ContactMessage
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

# Contact Form
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['fname', 'lname', 'email', 'subject', 'message']

# Sign-up Form
class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        validate_password(password)

        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)

# Contributor Submission Form (Bulk upload CSV)
class ContributorForm(forms.ModelForm):
    class Meta:
        model = Contributor
        fields = ['scientific_name', 'common_name', 'plant_description', 'csv_file', 'image']

# Contributor Submission Form (Manual Entry)      
class ManualPhytochemicalForm(forms.Form):
    scientific_name = forms.CharField(max_length=255)
    common_name = forms.CharField(max_length=255, required=False)
    plant_description = forms.CharField(widget=forms.Textarea, required=False)

    compound_name = forms.CharField(max_length=255)
    compound_class = forms.CharField(max_length=255, required=False)
    smiles = forms.CharField(widget=forms.Textarea, required=False)

# Diffdock form
class DockingForm(forms.Form):
    job_name = forms.CharField(max_length=200)
    email = forms.EmailField()

    protein_pdb = forms.FileField(
        help_text="Upload protein PDB file"
    )

    ligand_file = forms.FileField(
        required=False,
        help_text="Upload ligand file (mol2 or sdf)"
    )

    ligand_smiles = forms.CharField(
        required=False,
        widget=forms.Textarea,
        help_text="OR paste SMILES string"
    )

    num_poses = forms.IntegerField(min_value=1, max_value=100, initial=20)
    steps = forms.IntegerField(min_value=1, max_value=18, initial=18)
    save_trajectory = forms.BooleanField(required=False)

    def clean(self):
        cleaned = super().clean()
        ligand_file = cleaned.get("ligand_file")
        ligand_smiles = cleaned.get("ligand_smiles")

        if not ligand_file and not ligand_smiles:
            raise forms.ValidationError(
                "You must provide either a ligand file or a SMILES string."
            )

        if ligand_file and ligand_smiles:
            raise forms.ValidationError(
                "Provide only one: ligand file OR SMILES."
            )

        return cleaned
