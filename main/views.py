import csv
from io import TextIOWrapper
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

from .models import Contributor, Plant, Phytochemical, ScientificLiterature, DockingJob, ContributionAudit, ContributorLiterature, ContributorPhytochemical
from .forms import ContactForm, SignUpForm, LoginForm, ContributorForm, DockingForm
# from .tasks import run_diffdock
from .utils import compute_lipinski_from_smiles, normalize_header, run_diffdock, smiles_to_sdf, normalize_chemical_name

def is_manager(user):
    return user.is_superuser or user.groups.filter(name="Manager").exists()

def create_or_update_plant_from_contribution(contrib):
    """
    Migrates an approved Contributor entry into canonical
    Plant, Phytochemical, and ScientificLiterature tables.
    """

    with transaction.atomic():
        # Plant 
        plant, created = Plant.objects.get_or_create(
            scientific_name=contrib.scientific_name,
            defaults={
                "common_names": contrib.common_name or "",
                "description": contrib.plant_description or "",
                "image": contrib.image,
                "status": "approved",
                "contributor": contrib,
            },
        )

        if not created:
            plant.common_names = contrib.common_name or plant.common_names
            plant.description = contrib.plant_description or plant.description
            plant.image = contrib.image or plant.image
            plant.status = "approved"
            plant.save()

        # Track existing compound names to avoid duplicates
        existing_compounds = {c.compound_name.lower() for c in plant.phytochemicals.all()}

        # CSV 
        if contrib.csv_file:
            csv_file = TextIOWrapper(contrib.csv_file.open(), encoding="utf-8")
            reader = csv.DictReader(csv_file)

            normalized_rows = []
            for row in reader:
                normalized = {normalize_header(k): v for k, v in row.items()}
                normalized_rows.append(normalized)

            for row in normalized_rows:
                raw_name = (row.get("compound name") or "").strip()
                compound_name = normalize_chemical_name(raw_name)
                compound_class = (row.get("compound class") or "").strip()

                if not compound_name or compound_name.lower() in existing_compounds:
                    continue

                data = enrich_compound_from_name(compound_name)
                # compound_class = (row.get("Compound Class") or "").strip()

                Phytochemical.objects.create(
                    plant=plant,
                    compound_name=compound_name,
                    compound_class=compound_class,
                    smiles=data.get("smiles", ""),
                    pubchem_cid=data.get("pubchem_cid", ""),
                    inchikey=data.get("inchikey", ""),
                    molecular_weight=data.get("molecular_weight"),
                    logp=data.get("logp"),
                    h_donors=data.get("h_donors"),
                    h_acceptors=data.get("h_acceptors"),
                    lipinski_pass=data.get("lipinski_pass"),
                )
                existing_compounds.add(compound_name.lower())

        # Manual 
        elif contrib.manual_phytochemicals.exists():
            for cp in contrib.manual_phytochemicals.all():
                raw_name  = (cp.compound_name or "").strip()
                compound_name = normalize_chemical_name(raw_name)
                if not compound_name or compound_name.lower() in existing_compounds:
                    continue

                compound_class = (cp.compound_class or "").strip()
                data = enrich_compound_from_name(compound_name)

                Phytochemical.objects.create(
                    plant=plant,
                    compound_name=compound_name,
                    compound_class=compound_class,
                    smiles=data.get("smiles", ""),
                    pubchem_cid=data.get("pubchem_cid", ""),
                    inchikey=data.get("inchikey", ""),
                    molecular_weight=data.get("molecular_weight"),
                    logp=data.get("logp"),
                    h_donors=data.get("h_donors"),
                    h_acceptors=data.get("h_acceptors"),
                    lipinski_pass=data.get("lipinski_pass"),
                )
                existing_compounds.add(compound_name.lower())

        #  Literature 
        for lit in contrib.manual_literature.all():
            ScientificLiterature.objects.get_or_create(
                plant=plant,
                title=lit.title,
                defaults={
                    "authors": lit.authors,
                    "journal": lit.journal,
                    "doi": lit.doi,
                },
            )

        return plant

# Public Views

def index(request):
    search_query = request.GET.get("search", "")
    plants = Plant.objects.filter(status="approved").order_by("-submitted_at")

    if search_query:
        plants = plants.filter(
            Q(scientific_name__icontains=search_query) |
            Q(common_names__icontains=search_query) |
            Q(contributor__accession_number__icontains=search_query)
        )

    paginator = Paginator(plants, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "plants_exist": plants.exists(),
        "paginator": paginator,
    }
    return render(request, "index.html", context)


def plant_detail(request, pk):
    plant = get_object_or_404(Plant, pk=pk, status='approved')
    return render(request, 'plant_detail.html', {
        'plant': plant,
        'phytochemicals': plant.phytochemicals.all(),
        'literature': plant.literature.all(),
    })


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()

            fname = form.cleaned_data['fname']
            lname = form.cleaned_data['lname']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            send_mail(
                subject=f"AfroPhyto Contact: {subject}",
                message=f"From: {fname} {lname}\nEmail: {email}\n\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False
            )

            messages.success(request, "Your message has been sent successfully. We will get back to you shortly!")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})


def documentation(request):
    return render(request, 'documentation.html')


def data_license(request):
    return render(request, 'data_license.html')


def contributor_agreement(request):
    return render(request, 'contributor_agreement.html')


def team(request):
    return render(request, 'team.html')

# Authentication
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            contributor_group, _ = Group.objects.get_or_create(name='Contributor')
            user.groups.add(contributor_group)
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
        else:
            for error in form.non_field_errors():
                messages.error(request, error, extra_tags="password-mismatch")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60*60*24*30)
            return redirect("dashboard")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard
@login_required
def dashboard_view(request):
    if is_manager(request.user):
        return redirect("review_contributions")
    contributions = request.user.contributions.all().order_by('-created_at')
    return render(request, "dashboard.html", {
        "contributions": contributions,
        "total_contributions": contributions.count(),
        "pending_contributions": contributions.filter(status="pending").count(),
        "approved_contributions": contributions.filter(status="approved").count(),
        "is_manager": False,
    })

# Contributor Submission
def contribute(request):
    if request.method == "POST":
        form = ContributorForm(request.POST, request.FILES)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.user = request.user
            contribution.status = "pending"
            contribution.save()

            # Manual phytochemicals
            names = request.POST.getlist("compound_name")
            classes = request.POST.getlist("compound_class")

            seen = set()
            for n, c in zip(names, classes):
                name_clean = n.strip()
                if not name_clean or name_clean.lower() in seen:
                    continue
                seen.add(name_clean.lower())

                data = enrich_compound_from_name(name_clean)

                ContributorPhytochemical.objects.create(
                    contribution=contribution,
                    compound_name=name_clean,
                    compound_class=c.strip(),
                    smiles=data.get("smiles", "")
                )

            # Manual literature
            titles = request.POST.getlist("literature_title")
            authors_list = request.POST.getlist("literature_authors")
            journals = request.POST.getlist("literature_journal")
            dois = request.POST.getlist("literature_doi")

            for t, a, j, d in zip(titles, authors_list, journals, dois):
                if t.strip():
                    ContributorLiterature.objects.create(
                        contribution=contribution,
                        title=t.strip(),
                        authors=a.strip(),
                        journal=j.strip(),
                        doi=d.strip()
                    )

            messages.success(request, "Contribution submitted for review.")
            return redirect("dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContributorForm()

    return render(request, "contribute.html", {"form": form})

# Contribution Review
@login_required
@user_passes_test(is_manager)
def review_contributions(request):
    status = request.GET.get("status")
    qs = Contributor.objects.all().order_by("-created_at")
    if status in ["pending", "approved", "rejected"]:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "review_contributions.html", {
        "contributions": page_obj,
        "current_status": status or "all",
    })

@login_required
@user_passes_test(is_manager)
def approve_contribution(request, contrib_id):
    contrib = get_object_or_404(Contributor, id=contrib_id)
    if contrib.status == "approved":
        return redirect("review_contributions")

    contrib.status = "approved"
    contrib.save()

    ContributionAudit.objects.create(
        contribution=contrib,
        reviewer=request.user,
        action="approved",
        note=(
            f"Approved with "
            f"{contrib.manual_phytochemicals.count()} compounds and "
            f"{contrib.manual_literature.count()} literature records."
        )
    )

    create_or_update_plant_from_contribution(contrib)

    send_mail(
        subject="Contribution Approved",
        message=f"Hi {contrib.user.username},\n\n"
                f"Your contribution '{contrib.scientific_name}' has been approved and is now live on AfroPhyto.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[contrib.user.email],
        fail_silently=True,
    )

    return redirect("review_contributions")


@login_required
@user_passes_test(is_manager)
def reject_contribution(request, contrib_id):
    contrib = get_object_or_404(Contributor, id=contrib_id)
    note = request.POST.get("note", "").strip()
    if not note:
        messages.error(request, "Rejection requires a reason.")
        return redirect("contribution_detail", contrib_id=contrib.id)

    contrib.status = "rejected"
    contrib.save()

    ContributionAudit.objects.create(
        contribution=contrib,
        reviewer=request.user,
        action="rejected",
        note=note
    )

    send_mail(
        "Contribution Rejected",
        f"Hi {contrib.user.username},\n\nYour contribution was rejected for the following reason:\n\n{note}",
        settings.DEFAULT_FROM_EMAIL,
        [contrib.user.email],
        fail_silently=True,
    )

    return redirect("review_contributions")

# Contribution Detail
@login_required
def contribution_detail(request, contrib_id):
    contrib = get_object_or_404(Contributor, id=contrib_id)

    # Access control
    if not is_manager(request.user) and contrib.user != request.user:
        messages.error(request, "Unauthorized access.")
        return redirect("dashboard")

    # Load CSV rows
    csv_rows = []
    if contrib.csv_file:
        try:
            with TextIOWrapper(contrib.csv_file.open(), encoding="utf-8") as f:
                reader = csv.DictReader(f)
                csv_rows = list(reader)
        except Exception:
            csv_rows = []

    manual_phytos = contrib.manual_phytochemicals.all()
    manual_literature = contrib.manual_literature.all()
    audits = contrib.audits.select_related("reviewer").order_by("-timestamp")

    # Handle manager approval/rejection
    if request.method == "POST" and is_manager(request.user):
        action = request.POST.get("action")
        note = request.POST.get("note", "").strip()
        if action not in ["approved", "rejected"]:
            messages.error(request, "Invalid action.")
            return redirect("contribution_detail", contrib_id=contrib.id)
        if not note:
            messages.error(request, "Reviewer note is required.")
            return redirect("contribution_detail", contrib_id=contrib.id)

        contrib.status = action
        contrib.save()

        ContributionAudit.objects.create(
            contribution=contrib,
            reviewer=request.user,
            action=action,
            note=note
        )

        if action == "approved":
            create_or_update_plant_from_contribution(contrib)

        send_mail(
            subject=f"Contribution {action.capitalize()}",
            message=f"Hi {contrib.user.username},\n\n"
                    f"Your contribution '{contrib.scientific_name}' has been {action}.\n\n"
                    f"Reviewer note: {note}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contrib.user.email],
            fail_silently=True
        )

        messages.success(request, f"Contribution {action} successfully.")
        return redirect("review_contributions")

    return render(request, "contribution_detail.html", {
        "contrib": contrib,
        "csv_rows": csv_rows,
        "manual_phytos": manual_phytos,
        "manual_literature": manual_literature,
        "audits": audits,
        "is_manager": is_manager(request.user),
    })

# Export CSV
def export_plant_phytochemicals_csv(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id, status="approved")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{plant.scientific_name}_phytochemicals.csv"'
    writer = csv.writer(response)
    writer.writerow([
    "Plant",
    "Compound",
    "Class",
    "SMILES",
    "PubChem CID",
    "InChIKey",
    "Molecular Weight",
    "LogP",
    "H Donors",
    "H Acceptors",
    "Lipinski Pass"
])
    for p in plant.phytochemicals.all():
        writer.writerow([
    plant.scientific_name,
    p.compound_name,
    p.compound_class,
    p.smiles,
    p.pubchem_cid,
    p.inchikey,
    p.molecular_weight,
    p.logp,
    p.h_donors,
    p.h_acceptors,
    p.lipinski_pass
])
    return response

# NVIDIA Diffdock
def docking_with_diffdock(request):
    pass

def docking_submitted(request, job_id):
    job = get_object_or_404(DockingJob, job_id=job_id)
    return render(request, "docking_submitted.html", {"job_name": job.job_name, "email": job.email})


def docking_status(request, job_id):
    job = get_object_or_404(DockingJob, job_id=job_id)
    if job.completed:
        return redirect("docking_results", job_id=job.job_id)
    return render(request, "docking_pending.html", {"job": job})


def docking_results(request, job_id):
    job = get_object_or_404(DockingJob, job_id=job_id)
    if not job.completed:
        return render(request, "docking_pending.html", {"job": job})
    
    first_pose = job.poses.first() if hasattr(job, 'poses') else None
    pdb_data = first_pose.structure_text if first_pose else ""
    return render(request, "docking_results.html", {
        "job_name": job.job_name,
        "results": job,
        "pdb_data": pdb_data
    })
