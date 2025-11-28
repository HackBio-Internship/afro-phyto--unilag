from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Contributor, Plant, Phytochemical, ScientificLiterature
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import csv
from io import TextIOWrapper

# Create your views here.
def index(request):
    search_query = request.GET.get('search', '')

    # Filter plants based on search
    plants = Plant.objects.all().order_by('scientific_name')
    if search_query:
        plants = plants.filter(
            Q(scientific_name__icontains=search_query) |
            Q(common_names__icontains=search_query)
        )

    # Pagination
    page = request.GET.get("page", 1)
    try:
        page = int(page)
        if page < 1:
            page = 1
    except:
        page = 1

    paginator = Paginator(plants, 10)

    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "index.html", {
        "page_obj": page_obj,
        "search_query": search_query,
    })

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        messages.success(request, 'Your message has been sent. Thank you!')
        return redirect('contact')
    return render(request, 'contact.html')

def documentation(request):
    return render(request, 'documentation.html')

def team(request):
    return render(request, 'team.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('signup')
        user = User.objects.create_user(username=username, email=email, password=password, first_name=fullname)
        Contributor.objects.create(user=user)
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('contribute')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required(login_url='login')
def contribute(request):
    if request.method == 'POST':
        user = request.user
        contributor = Contributor.objects.get(user=user)

        # Handle bulk CSV upload
        csv_file = request.FILES.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Uploaded file is not CSV.')
                return redirect('contribute')

            try:
                file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
                reader = csv.DictReader(file_data)
                for row in reader:
                    plant = Plant.objects.create(
                        scientific_name=row.get('Scientific Name', ''),
                        common_names=row.get('Common Name(s)', ''),
                        description=row.get('Plant Description', ''),
                        contributor=contributor,
                    )
                    # For simplicity, assume compounds and literature are separated by semicolons
                    compounds = row.get('Compounds', '').split(';')
                    for compound_str in compounds:
                        parts = compound_str.split('|')  # Assuming format CompoundName|Class|Activity
                        if len(parts) == 3:
                            Phytochemical.objects.create(
                                plant=plant,
                                compound_name=parts[0].strip(),
                                compound_class=parts[1].strip(),
                                biological_activity=parts[2].strip(),
                            )
                # Similarly parse literature if included in CSV
                messages.success(request, 'CSV data uploaded successfully.')
                return redirect('contribute')
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
                return redirect('contribute')

        # Handle manual form submission
        scientific_name = request.POST.get('scientific_name')
        common_names = request.POST.get('common_names')
        description = request.POST.get('description')

        plant = Plant.objects.create(
            scientific_name=scientific_name,
            common_names=common_names,
            description=description,
            contributor=contributor,
        )

        # Save compounds (multiple)
        compound_names = request.POST.getlist('compound_name')
        compound_classes = request.POST.getlist('compound_class')
        biological_activities = request.POST.getlist('biological_activity')

        for name, cls, activity in zip(compound_names, compound_classes, biological_activities):
            if name.strip():
                Phytochemical.objects.create(
                    plant=plant,
                    compound_name=name,
                    compound_class=cls,
                    biological_activity=activity,
                )

        # Save literature
        title = request.POST.get('literature_title')
        authors = request.POST.get('literature_authors')
        journal = request.POST.get('literature_journal')
        doi = request.POST.get('literature_doi')

        if title:
            ScientificLiterature.objects.create(
                plant=plant,
                title=title,
                authors=authors,
                journal=journal,
                doi=doi,
            )

        messages.success(request, 'Plant and related data submitted successfully. Await review.')
        return redirect('contribute')

    return render(request, 'contribute.html')

def data_license(request):
    return render(request, 'data_license.html')

def contributor_agreement(request):
    return render(request, 'contibutor_agreement.html')
