from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.files import File
import json
from xhtml2pdf import pisa
from io import BytesIO
import os
import base64
from .models import AcceptationAudit, Sharehol, Branche, Manager
from account.models import Profile
from .forms import (
    AcceptationAuditForm, ShareholFormSet, BrancheFormSet, ManagerFormSet,
    AuditStep1Form, AuditStep2Form, AuditStep3Form, AuditStep7Form,
    AuditStep8Form, AuditStep9Form, AuditStep10Form, AuditStep11Form,
    AuditStep12Form, AuditStep13Form, AuditStep15Form, AuditConclusionForm
)

# Fonction pour vérifier si les étapes précédentes sont validées
def check_previous_steps(audit, current_step):
    """
    Vérifie que toutes les étapes précédentes sont validées
    
    Args:
        audit: L'instance AcceptationAudit
        current_step: Le numéro de l'étape courante
    
    Returns:
        tuple: (is_valid, first_invalid_step)
            - is_valid: True si toutes les étapes précédentes sont validées
            - first_invalid_step: Le numéro de la première étape non validée (None si toutes sont validées)
    """
    # Ne pas vérifier pour l'étape 1
    if current_step == 1:
        return True, None
    
    # Vérifier toutes les étapes précédentes
    for step_num in range(1, current_step):
        step_field = getattr(audit, f'step_{step_num}', False)
        if not step_field:
            return False, step_num
    
    return True, None

# Create your views here.

def login_view(request):
    """
    Vue de connexion pour les utilisateurs
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')  # Rediriger vers le dashboard si déjà connecté
    
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        if username_or_email and password:
            # 1) Essayer directement avec ce qui est saisi (username)
            user = authenticate(request, username=username_or_email, password=password)
            
            # 2) Si échec, tenter via email -> retrouver le username et ré-authentifier
            if user is None and '@' in username_or_email:
                try:
                    # email case-insensitive
                    matched_user = User.objects.filter(email__iexact=username_or_email).first()
                    if matched_user:
                        user = authenticate(request, username=matched_user.username, password=password)
                except Exception:
                    user = None

            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Bienvenue, {user.first_name or user.username}!')
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Identifiants invalides. Vérifiez votre nom d\'utilisateur/email et mot de passe.')
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')
    
    return render(request, 'core/login.html')

@login_required
def logout_view(request):
    """
    Vue de déconnexion
    """
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')

@login_required
def dashboard(request):
    """
    Vue du tableau de bord principal
    """
    # Récupérer les audits créés par l'utilisateur connecté
    user_audits = AcceptationAudit.objects.filter(done_by=request.user).order_by('-date_added')
    user_audits_drafts = user_audits.filter(is_published=False)
    user_audits_sent = user_audits.filter(is_published=True)
    
    # Récupérer les audits où l'utilisateur est le reviewer (reviewed_by)
    # Uniquement pour les utilisateurs avec le statut "associate"
    reviews_audits = None
    reviews_audits_count = 0
    reviews_audits_all = None
    reviews_audits_done = None
    if hasattr(request.user, 'profile') and request.user.profile.status == 'associate':
        reviews_qs = AcceptationAudit.objects.filter(reviewed_by=request.user).order_by('-date_published')
        reviews_audits_all = reviews_qs
        reviews_audits = reviews_qs.filter(is_reviewed=False)
        reviews_audits_done = reviews_qs.filter(is_reviewed=True)
        reviews_audits_count = reviews_audits.count()
    
    # Récupérer les audits où l'utilisateur est le signataire (signed_by)
    # Uniquement si l'audit est publié et révisé
    signed_qs = AcceptationAudit.objects.filter(
        signed_by=request.user,
        is_published=True,
        is_reviewed=True,
    ).order_by('-reviewed_at')
    signed_audits_all = signed_qs
    signed_audits = signed_qs.filter(is_signed=False)
    signed_audits_done = signed_qs.filter(is_signed=True)
    signed_audits_count = signed_audits.count()
    
    context = {
        'user': request.user,
        'total_audits': AcceptationAudit.objects.count(),
        'user_audits': user_audits,
        'user_audits_count': user_audits.count(),
        'user_audits_drafts': user_audits_drafts,
        'user_audits_sent': user_audits_sent,
        'reviews_audits': reviews_audits,
        'reviews_audits_count': reviews_audits_count,
        'reviews_audits_all': reviews_audits_all,
        'reviews_audits_done': reviews_audits_done,
        'signed_audits': signed_audits,
        'signed_audits_count': signed_audits_count,
        'signed_audits_all': signed_audits_all,
        'signed_audits_done': signed_audits_done,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def create_audit_view(request):
    """
    Vue pour créer un nouvel audit
    """
    if request.method == 'POST':
        form = AcceptationAuditForm(request.POST)
        sharehol_formset = ShareholFormSet(request.POST)
        branche_formset = BrancheFormSet(request.POST)
        manager_formset = ManagerFormSet(request.POST)
        
        if form.is_valid() and sharehol_formset.is_valid() and branche_formset.is_valid() and manager_formset.is_valid():
            audit = form.save(commit=False)
            audit.done_by = request.user
            audit.save()
            
            # Sauvegarder les formsets
            sharehol_formset.instance = audit
            sharehol_formset.save()
            
            branche_formset.instance = audit
            branche_formset.save()
            
            manager_formset.instance = audit
            manager_formset.save()
            
            messages.success(request, 'Audit créé avec succès!')
            return redirect('core:audit_detail', pk=audit.pk)
    else:
        form = AcceptationAuditForm()
        sharehol_formset = ShareholFormSet()
        branche_formset = BrancheFormSet()
        manager_formset = ManagerFormSet()
    
    context = {
        'form': form,
        'sharehol_formset': sharehol_formset,
        'branche_formset': branche_formset,
        'manager_formset': manager_formset,
    }
    return render(request, 'core/create_audit.html', context)

@login_required
def audit_detail_view(request, pk):
    """
    Vue pour afficher les détails d'un audit
    """
    # Récupérer l'audit - autoriser l'accès si :
    # 1. L'utilisateur est le créateur (done_by)
    # 2. OU l'utilisateur est le reviewer ET l'audit est publié
    try:
        audit = AcceptationAudit.objects.get(
            pk=pk,
        )
        
        # Vérifier les permissions
        is_creator = audit.done_by == request.user
        is_reviewer = audit.is_published and audit.reviewed_by == request.user
        # Le signed_by peut accéder seulement si l'audit est révisé (is_reviewed = True)
        is_signed_by_user = audit.is_reviewed and audit.signed_by == request.user if audit.signed_by else False
        
        if not (is_creator or is_reviewer or is_signed_by_user):
            messages.error(request, 'Vous n\'avez pas l\'autorisation d\'accéder à cet audit.')
            return redirect('core:dashboard')
            
    except AcceptationAudit.DoesNotExist:
        messages.error(request, 'Cet audit n\'existe pas.')
        return redirect('core:dashboard')
    
    shareholders = audit.acceptation_audit_shareholder.filter(deleted=False)
    branches = audit.acceptation_audit_branche.filter(deleted=False)
    managers = audit.acceptation_audit_manager.filter(deleted=False)
    
    # Calculer les totaux pour les actionnaires
    total_quantity_held = sum(sh.quantity_held for sh in shareholders)
    total_percentage_held = sum(sh.percentage_held for sh in shareholders)
    total_quantity_vote = sum(sh.quantity_vote for sh in shareholders)
    total_percentage_vote = sum(sh.percentage_vote for sh in shareholders)
    
    # Calculer les totaux pour les filiales
    total_cac_auditor = sum(b.cac_auditor for b in branches)
    total_ownership_percentage = sum(b.ownership_percentage for b in branches)
    total_control_percentage = sum(b.control_percentage for b in branches)
    
    # Récupérer les profiles du département Audit
    audit_profiles = Profile.objects.filter(departement='audit', status='associate', deleted=False).select_related('user')
    
    # Déterminer si l'utilisateur est le créateur, le reviewer ou le signataire
    is_creator = audit.done_by == request.user
    is_reviewer = audit.is_published and audit.reviewed_by == request.user
    is_signed_by = audit.signed_by == request.user if audit.signed_by else False
    
    context = {
        'audit': audit,
        'shareholders': shareholders,
        'branches': branches,
        'managers': managers,
        'total_quantity_held': total_quantity_held,
        'total_percentage_held': total_percentage_held,
        'total_quantity_vote': total_quantity_vote,
        'total_percentage_vote': total_percentage_vote,
        'total_cac_auditor': total_cac_auditor,
        'total_ownership_percentage': total_ownership_percentage,
        'total_control_percentage': total_control_percentage,
        'audit_profiles': audit_profiles,
        'is_creator': is_creator,
        'is_reviewer': is_reviewer,
        'is_signed_by': is_signed_by,
    }
    return render(request, 'core/audit_detail.html', context)

@login_required
def audit_list_view(request):
    """
    Vue pour lister tous les audits
    """
    audits = AcceptationAudit.objects.all().order_by('-date_added')
    context = {
        'audits': audits,
    }
    return render(request, 'core/audit_list.html', context)

@login_required
@require_POST
def publish_audit_view(request, pk):
    """
    Vue pour publier un audit et envoyer une notification par email
    """
    try:
        audit = AcceptationAudit.objects.get(pk=pk, done_by=request.user)
    except AcceptationAudit.DoesNotExist:
        messages.error(request, 'Vous n\'avez pas l\'autorisation d\'accéder à cet audit.')
        return redirect('core:dashboard')
    
    # Vérifier que toutes les étapes sont validées
    if not audit.step_13:
        messages.error(request, 'Vous devez compléter toutes les étapes avant de publier l\'audit.')
        return redirect('core:audit_detail', pk=audit.pk)
    
    # Vérifier si l'audit est déjà publié
    if audit.is_published:
        messages.warning(request, 'Cet audit a déjà été publié.')
        return redirect('core:audit_detail', pk=audit.pk)
    
    # Récupérer les données du formulaire
    recipient_id = request.POST.get('recipient_id')
    message = request.POST.get('message', '').strip()
    
    if not recipient_id:
        messages.error(request, 'Veuillez sélectionner un destinataire.')
        return redirect('core:audit_detail', pk=audit.pk)
    
    try:
        recipient_profile = Profile.objects.get(pk=recipient_id, departement='audit', status='associate', deleted=False)
    except Profile.DoesNotExist:
        messages.error(request, 'Le profil sélectionné n\'existe pas ou n\'appartient pas au département Audit.')
        return redirect('core:audit_detail', pk=audit.pk)
    
    # Publier l'audit
    audit.is_published = True
    audit.date_published = timezone.now()
    audit.reviewed_by = recipient_profile.user
    audit.save()
    
    # Construire l'URL absolue pour le lien vers la page de détail de l'audit
    audit_detail_url = request.build_absolute_uri(reverse('core:audit_detail', kwargs={'pk': audit.pk}))
    
    # Préparer l'email
    recipient_email = recipient_profile.user.email
    subject = f'Nouvel audit publié - {audit.reference}'
    
    email_body = f"""
Bonjour {recipient_profile.user.get_full_name() or recipient_profile.user.username},

Un nouvel audit a été  :

Référence : {audit.reference}
Client : {audit.client}
Exercice : {audit.exercice}
Créé par : {audit.done_by.get_full_name() or audit.done_by.username}
Date envoiyée : {audit.date_published.strftime('%d/%m/%Y %H:%M')}

{f'Message :\n{message}' if message else ''}

Vous pouvez consulter les détails de l'audit en cliquant sur le lien suivant :
{audit_detail_url}

Cordialement,
MOORE SÉNÉGAL
"""
    
    # Envoyer l'email (en mode console pour le développement)
    try:
        send_mail(
            subject=subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        messages.success(request, f'Formulaire envoyé avec succès! Une notification a été envoyée à {recipient_profile.user.get_full_name() or recipient_profile.user.username}.')
    except Exception as e:
        # Même en cas d'erreur d'envoi d'email, on garde la publication
        messages.warning(request, f'Formulaire envoyé mais une erreur est survenue lors de l\'envoi de l\'email: {str(e)}')
    
    return redirect('core:audit_detail', pk=audit.pk)

@login_required
def audit_pdf_view(request, pk):
    """
    Vue pour générer et télécharger l'audit en PDF
    """
    try:
        audit = AcceptationAudit.objects.get(
            pk=pk,
        )
        
        # Vérifier les permissions
        is_creator = audit.done_by == request.user
        is_reviewer = audit.is_published and audit.reviewed_by == request.user
        # Le signed_by peut accéder seulement si l'audit est révisé (is_reviewed = True)
        is_signed_by_user = audit.is_reviewed and audit.signed_by == request.user if audit.signed_by else False
        
        if not (is_creator or is_reviewer or is_signed_by_user):
            messages.error(request, 'Vous n\'avez pas l\'autorisation d\'accéder à cet audit.')
            return redirect('core:dashboard')
            
    except AcceptationAudit.DoesNotExist:
        messages.error(request, 'Cet audit n\'existe pas.')
        return redirect('core:dashboard')
    
    # Récupérer les données associées
    shareholders = audit.acceptation_audit_shareholder.filter(deleted=False)
    branches = audit.acceptation_audit_branche.filter(deleted=False)
    managers = audit.acceptation_audit_manager.filter(deleted=False)
    
    # Calculer les totaux
    total_quantity_held = sum(sh.quantity_held for sh in shareholders)
    total_percentage_held = sum(sh.percentage_held for sh in shareholders)
    total_quantity_vote = sum(sh.quantity_vote for sh in shareholders)
    total_percentage_vote = sum(sh.percentage_vote for sh in shareholders)
    total_cac_auditor = sum(b.cac_auditor for b in branches)
    total_ownership_percentage = sum(b.ownership_percentage for b in branches)
    total_control_percentage = sum(b.control_percentage for b in branches)
    
    # Préparer les verbose_name des questions pour le template
    questions_data = []
    for i in range(1, 84):
        question_field_name = f'question_{i}'
        response_field_name = f'response_{i}'
        if hasattr(audit, question_field_name):
            field = audit._meta.get_field(question_field_name)
            questions_data.append({
                'number': i,
                'verbose_name': field.verbose_name,
                'value': getattr(audit, question_field_name, ''),
                'response': getattr(audit, response_field_name, '') if hasattr(audit, response_field_name) else '',
            })
    
    # Préparer signature (affichage seulement pour signed_by)
    # Convertir l'image en base64 pour l'inclure dans le PDF
    signature_base64 = None
    if audit.is_signed and audit.senior_signature:
        try:
            # Ouvrir l'image et la convertir en base64
            signature_file = audit.senior_signature.open()
            signature_data = signature_file.read()
            signature_file.close()
            
            # Obtenir l'extension du fichier
            ext = audit.senior_signature.name.split('.')[-1].lower()
            if ext == 'jpg':
                ext = 'jpeg'
            
            # Encoder en base64
            signature_base64 = base64.b64encode(signature_data).decode('utf-8')
            signature_base64 = f"data:image/{ext};base64,{signature_base64}"
        except Exception:
            signature_base64 = None

    context = {
        'audit': audit,
        'shareholders': shareholders,
        'branches': branches,
        'managers': managers,
        'total_quantity_held': total_quantity_held,
        'total_percentage_held': total_percentage_held,
        'total_quantity_vote': total_quantity_vote,
        'total_percentage_vote': total_percentage_vote,
        'total_cac_auditor': total_cac_auditor,
        'total_ownership_percentage': total_ownership_percentage,
        'total_control_percentage': total_control_percentage,
        'questions_data': questions_data,
        # Flags d'accès à la conclusion
        'is_reviewer': is_reviewer,
        'is_signed_by': is_signed_by_user,
        'signature_base64': signature_base64,
    }
    
    # Rendre le template HTML PDF simple
    html_content = render_to_string('core/audit_detail_pdf.html', context)
    
    # Générer le PDF avec xhtml2pdf
    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
    pdf_file.seek(0)
    
    # Vérifier si le PDF a été créé correctement
    if pisa_status.err:
        messages.error(request, 'Erreur lors de la génération du PDF.')
        return redirect('core:audit_detail', pk=audit.pk)
    
    # Créer la réponse HTTP
    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="audit_{audit.reference}.pdf"'
    
    return response

# Vues pour le formulaire progressif
@login_required
def create_audit_step1(request):
    """
    Étape 1: Création de l'audit (client, reference, exercice)
    """
    if request.method == 'POST':
        form = AuditStep1Form(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.done_by = request.user
            audit.step_1 = True
            audit.save()
            messages.success(request, 'Audit créé avec succès!')
            return redirect('core:audit_step2', pk=audit.pk)
    else:
        form = AuditStep1Form()
    
    context = {
        'form': form,
        'step': 1,
        'total_steps': 15,
        'step_title': 'Informations de base',
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step2(request, pk):
    """
    Étape 2: Informations de l'entreprise
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que l'étape 1 est validée
    is_valid, invalid_step = check_previous_steps(audit, 2)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        form = AuditStep2Form(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            audit.step_2 = True
            audit.save()
            messages.success(request, 'Étape 2 sauvegardée!')
            return redirect('core:audit_step3', pk=audit.pk)
    else:
        form = AuditStep2Form(instance=audit)
    
    context = {
        'form': form,
        'audit': audit,
        'step': 2,
        'total_steps': 15,
        'step_title': 'I.1. Informations sur l\'entité',
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step3(request, pk):
    """
    Étape 3: Informations de la mission
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 3)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        form = AuditStep3Form(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            audit.step_3 = True
            audit.save()
            messages.success(request, 'Étape 3 sauvegardée!')
            return redirect('core:audit_step4', pk=audit.pk)
    else:
        form = AuditStep3Form(instance=audit)
    
    context = {
        'form': form,
        'audit': audit,
        'step': 3,
        'total_steps': 15,
        'step_title': 'I.2.	Informations sur la mission',
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step4(request, pk):
    """
    Étape 4: Actionnaires
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 4)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        formset = ShareholFormSet(request.POST, instance=audit)
        if formset.is_valid():
            formset.save()
            audit.step_4 = True
            audit.save()
            messages.success(request, 'Étape 4 sauvegardée!')
            return redirect('core:audit_step5', pk=audit.pk)
    else:
        formset = ShareholFormSet(instance=audit)
    
    context = {
        'formset': formset,
        'audit': audit,
        'step': 4,
        'total_steps': 15,
        'step_title': 'I.3.	Informations sur l\'actionnariat',
        'formset_type': 'sharehol'
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step5(request, pk):
    """
    Étape 5: Filiales
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 5)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        formset = BrancheFormSet(request.POST, instance=audit)
        if formset.is_valid():
            formset.save()
            audit.step_5 = True
            audit.save()
            messages.success(request, 'Étape 5 sauvegardée!')
            return redirect('core:audit_step6', pk=audit.pk)
    else:
        formset = BrancheFormSet(instance=audit)
    
    context = {
        'formset': formset,
        'audit': audit,
        'step': 5,
        'total_steps': 15,
        'step_title': 'I.4.	Informations sur les filiales',
        'formset_type': 'branche'
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step6(request, pk):
    """
    Étape 6: Dirigeants
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 6)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        formset = ManagerFormSet(request.POST, instance=audit)
        if formset.is_valid():
            formset.save()
            audit.step_6 = True
            audit.save()
            messages.success(request, 'Étape 6 sauvegardée!')
            return redirect('core:audit_step7', pk=audit.pk)
    else:
        formset = ManagerFormSet(instance=audit)
    
    context = {
        'formset': formset,
        'audit': audit,
        'step': 6,
        'total_steps': 15,
        'step_title': 'I.5.	Informations sur les administrateurs et dirigeants',
        'formset_type': 'manager'
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step7(request, pk):
    """
    Étape 7: Questions 1-22
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 7)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        form = AuditStep7Form(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            audit.step_7 = True
            audit.save()
            messages.success(request, 'Étape 7 sauvegardée!')
            return redirect('core:audit_step8', pk=audit.pk)
    else:
        form = AuditStep7Form(instance=audit)
    
    context = {
        'form': form,
        'audit': audit,
        'step': 7,
        'total_steps': 15,
        'step_title': 'II.	Indépendance',
        'step_note': "Toute réponse <span>oui</span> accroit le risque et nécessite un commentaire indiquant s'il est possible de mettre en œuvre des mesures de sauvegarde, et si oui, lesquelles.",
        'questions_range': range(1, 23)
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step8(request, pk):
    """
    Étape 8: Questions 23-39
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 8)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        form = AuditStep8Form(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            audit.step_8 = True
            audit.save()
            messages.success(request, 'Étape 8 sauvegardée!')
            return redirect('core:audit_step9', pk=audit.pk)
    else:
        form = AuditStep8Form(instance=audit)
    
    context = {
        'form': form,
        'audit': audit,
        'step': 8,
        'total_steps': 15,
        'step_title': 'III.	Acceptation du client',
        'step_subtitle': "I.6. Identification du client ",
        'step_note': "Toute réponse <span>non</span> indique un problème pour l'acceptation de la mission.",
        'questions_range': range(23, 40)
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step9(request, pk):
    """
    Étape 9: Questions 40-46
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 9)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        form = AuditStep9Form(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            audit.step_9 = True
            audit.save()
            messages.success(request, 'Étape 9 sauvegardée!')
            return redirect('core:audit_step10', pk=audit.pk)
    else:
        form = AuditStep9Form(instance=audit)
    
    context = {
        'form': form,
        'audit': audit,
        'step': 9,
        'total_steps': 15,
        'step_title': 'I.7.	Prise en compte de l\'intégrité du client',
        'step_note': "Toute réponse <span>oui</span> accroit le risque",
        'questions_range': range(40, 47)
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step10(request, pk):
    """
    Étape 10: Questions 47-49
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 10)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        form = AuditStep10Form(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            audit.step_10 = True
            audit.save()
            messages.success(request, 'Étape 10 sauvegardée!')
            return redirect('core:audit_step11', pk=audit.pk)
    else:
        form = AuditStep10Form(instance=audit)
    
    context = {
        'form': form,
        'audit': audit,
        'step': 10,
        'total_steps': 15,
        'step_title': 'I.8.	Pratique des affaires',
        'step_note': "Toute réponse <span>oui</span> accroit le risque",
        'questions_range': range(47, 50)
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step11(request, pk):
    """
    Étape 11: Questions 50-60
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 11)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        form = AuditStep11Form(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            audit.step_11 = True
            audit.save()
            messages.success(request, 'Étape 11 sauvegardée!')
            return redirect('core:audit_step12', pk=audit.pk)
    else:
        form = AuditStep11Form(instance=audit)
    
    context = {
        'form': form,
        'audit': audit,
        'step': 11,
        'total_steps': 15,
        'step_title': 'IV.1. Procédure de nomination',
        'step_note': "A l'exception de la première question et de la dernière, toute réponse <span>oui</span> accroit le risque.",
        'questions_range': range(50, 61)
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step12(request, pk):
    """
    Étape 12: Questions 61-77
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 12)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        form = AuditStep12Form(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            audit.step_12 = True
            audit.save()
            messages.success(request, 'Étape 12 sauvegardée!')
            return redirect('core:audit_step13', pk=audit.pk)
    else:
        form = AuditStep12Form(instance=audit)
    
    context = {
        'form': form,
        'audit': audit,
        'step': 12,
        'total_steps': 14,
        'step_title': 'IV.2. Risques liés à la mission',
        'questions_range': range(61, 78)
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step13(request, pk):
    """
    Étape 13: Questions 78-83
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 13)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    if request.method == 'POST':
        form = AuditStep13Form(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            audit.step_13 = True
            audit.save()
            messages.success(request, 'Étape 13 sauvegardée!')
            return redirect('core:audit_step14', pk=audit.pk)
    else:
        form = AuditStep13Form(instance=audit)
    
    context = {
        'form': form,
        'audit': audit,
        'step': 13,
        'total_steps': 14,
        'step_title': 'Questions d\'audit (78-83)',
        'questions_range': range(78, 84)
    }
    return render(request, 'core/audit_step.html', context)

@login_required
def audit_step14(request, pk):
    """
    Étape 14: Finalisation et publication
    """
    audit = get_object_or_404(AcceptationAudit, pk=pk, done_by=request.user)
    
    # Vérifier que les étapes précédentes sont validées
    is_valid, invalid_step = check_previous_steps(audit, 14)
    if not is_valid:
        messages.error(request, f'Vous devez d\'abord compléter l\'étape {invalid_step}.')
        if invalid_step == 1:
            return redirect('core:create_audit_step1')
        return redirect('core:audit_step' + str(invalid_step), pk=pk)
    
    # Vérifier que toutes les étapes sont validées
    if not audit.step_13:
        messages.error(request, 'Vous devez compléter toutes les étapes avant de publier l\'audit.')
        return redirect('core:audit_step13', pk=audit.pk)
    
    # Si c'est une requête POST pour publier l'audit (depuis le modal)
    if request.method == 'POST' and 'publish' in request.POST:
        # Récupérer les données du formulaire
        recipient_id = request.POST.get('recipient_id')
        message = request.POST.get('message', '').strip()
        
        if not recipient_id:
            messages.error(request, 'Veuillez sélectionner un destinataire.')
            return redirect('core:audit_step14', pk=audit.pk)
        
        try:
            recipient_profile = Profile.objects.get(pk=recipient_id, departement='audit', status='associate', deleted=False)
        except Profile.DoesNotExist:
            messages.error(request, 'Le profil sélectionné n\'existe pas ou n\'appartient pas au département Audit.')
            return redirect('core:audit_step14', pk=audit.pk)
        
        # Vérifier si l'audit est déjà publié
        if audit.is_published:
            messages.warning(request, 'Cet audit a déjà été envoyé.')
            return redirect('core:audit_detail', pk=audit.pk)
        
        # Publier l'audit
        audit.is_published = True
        audit.date_published = timezone.now()
        audit.reviewed_by = recipient_profile.user
        audit.save()
        
        # Construire l'URL absolue pour le lien vers la page de détail de l'audit
        audit_detail_url = request.build_absolute_uri(reverse('core:audit_detail', kwargs={'pk': audit.pk}))
        
        # Préparer l'email
        recipient_email = recipient_profile.user.email
        subject = f'Nouvel audit publié - {audit.reference}'
        
        email_body = f"""
Bonjour {recipient_profile.user.get_full_name() or recipient_profile.user.username},

Une nouvelle mission d'acceptation a été envoyé pour revue :

Référence : {audit.reference}
Client : {audit.client}
Exercice : {audit.exercice}
Créé par : {audit.done_by.get_full_name() or audit.done_by.username}
Date envoyée : {audit.date_published.strftime('%d/%m/%Y %H:%M')}

{f'Message :\n{message}' if message else ''}

Vous pouvez consulter les détails du formulaire en cliquant sur le lien suivant :
{audit_detail_url}

Cordialement,
MOORE SÉNÉGAL
"""
        
        # Envoyer l'email (en mode console pour le développement)
        try:
            send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            messages.success(request, f'Audit envoyé avec succès! Une notification a été envoyée à {recipient_profile.user.get_full_name() or recipient_profile.user.username}.')
        except Exception as e:
            # Même en cas d'erreur d'envoi d'email, on garde la publication
            messages.warning(request, f'Audit envoyé mais une erreur est survenue lors de l\'envoi de l\'email: {str(e)}')
        
        return redirect('core:audit_detail', pk=audit.pk)
    
    # Récupérer les profiles du département Audit avec statut associate
    audit_profiles = Profile.objects.filter(departement='audit', status='associate', deleted=False).select_related('user')
    
    form = AuditStep15Form(instance=audit)
    
    context = {
        'form': form,
        'audit': audit,
        'step': 14,
        'total_steps': 14,
        'step_title': 'Finalisation',
        'is_final_step': True,
        'audit_profiles': audit_profiles,
    }
    return render(request, 'core/audit_step.html', context)


# Vues AJAX pour la suppression
@login_required
@require_POST
@csrf_exempt
def delete_shareholder(request, pk):
    """
    Vue AJAX pour supprimer un actionnaire
    """
    try:
        shareholder = get_object_or_404(Sharehol, pk=pk)
        shareholder.delete()  # Suppression définitive
        return JsonResponse({'success': True, 'message': 'Actionnaire supprimé avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
@csrf_exempt
def delete_branche(request, pk):
    """
    Vue AJAX pour supprimer une filiale
    """
    try:
        branche = get_object_or_404(Branche, pk=pk)
        branche.delete()  # Suppression définitive
        return JsonResponse({'success': True, 'message': 'Filiale supprimée avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
@csrf_exempt
def delete_manager(request, pk):
    """
    Vue AJAX pour supprimer un dirigeant
    """
    try:
        manager = get_object_or_404(Manager, pk=pk)
        manager.delete()  # Suppression définitive
        return JsonResponse({'success': True, 'message': 'Dirigeant supprimé avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
@csrf_exempt
def apply_signature_view(request, pk):
    """
    Vue AJAX pour appliquer la signature du signed_by à l'audit
    """
    try:
        audit = get_object_or_404(AcceptationAudit, pk=pk)
        
        # Vérifier que l'utilisateur est le signed_by et que l'audit est révisé
        if audit.signed_by != request.user:
            return JsonResponse({'success': False, 'error': 'Vous n\'avez pas l\'autorisation d\'appliquer votre signature à cet audit.'})
        
        if not audit.is_reviewed:
            return JsonResponse({'success': False, 'error': 'L\'audit doit être révisé avant de pouvoir être signé.'})
        
        # Récupérer le profil de l'utilisateur
        if not hasattr(request.user, 'profile'):
            return JsonResponse({'success': False, 'error': 'Vous n\'avez pas de profil. Veuillez contacter l\'administrateur.'})
        
        profile = request.user.profile
        
        # Vérifier que l'utilisateur a une signature
        if not profile.signature:
            return JsonResponse({'success': False, 'error': 'Vous n\'avez pas de signature enregistrée. Veuillez d\'abord créer votre signature.'})
        
        # Mettre à jour les champs
        # Copier l'image de la signature du profil vers l'audit
        if profile.signature:
            # Ouvrir le fichier source
            source_file = profile.signature.open()
            # Copier vers le champ ImageField de l'audit
            audit.senior_signature.save(
                profile.signature.name.split('/')[-1],  # Nom du fichier
                File(source_file),
                save=False
            )
            source_file.close()
        
        audit.is_signed = True
        audit.signed_at = timezone.now().date()
        audit.save()
        
        # Construire l'URL absolue pour le lien vers la page de détail de l'audit
        audit_detail_url = request.build_absolute_uri(reverse('core:audit_detail', kwargs={'pk': audit.pk}))
        
        # Envoyer un email de notification au créateur de l'audit (done_by)
        if audit.done_by and audit.done_by.email:
            creator_subject = f'Audit signé - {audit.reference}'
            creator_email_body = f"""
Bonjour {audit.done_by.get_full_name() or audit.done_by.username},

La mission d'acceptation a été signée :

Référence : {audit.reference}
Client : {audit.client}
Exercice : {audit.exercice}
Signé par : {request.user.get_full_name() or request.user.username}
Date de signature : {audit.signed_at.strftime('%d/%m/%Y')}

Vous pouvez consulter les détails du formulaire en cliquant sur le lien suivant :
{audit_detail_url}

Cordialement,
MOORE SÉNÉGAL
"""
            try:
                send_mail(
                    subject=creator_subject,
                    message=creator_email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[audit.done_by.email],
                    fail_silently=False,
                )
            except Exception as e:
                # En cas d'erreur d'envoi d'email, on continue quand même
                pass
        
        # Envoyer un email de notification au réviseur (reviewed_by)
        if audit.reviewed_by and audit.reviewed_by.email:
            reviewer_subject = f'Audit signé - {audit.reference}'
            reviewer_email_body = f"""
Bonjour {audit.reviewed_by.get_full_name() or audit.reviewed_by.username},

La mission d'acceptation que vous avez révisée a été signée :

Référence : {audit.reference}
Client : {audit.client}
Exercice : {audit.exercice}
Créé par : {audit.done_by.get_full_name() or audit.done_by.username}
Signé par : {request.user.get_full_name() or request.user.username}
Date de signature : {audit.signed_at.strftime('%d/%m/%Y')}

Vous pouvez consulter les détails du formulaire en cliquant sur le lien suivant :
{audit_detail_url}

Cordialement,
MOORE SÉNÉGAL
"""
            try:
                send_mail(
                    subject=reviewer_subject,
                    message=reviewer_email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[audit.reviewed_by.email],
                    fail_silently=False,
                )
            except Exception as e:
                # En cas d'erreur d'envoi d'email, on continue quand même
                pass
        
        return JsonResponse({
            'success': True,
            'message': 'Signature appliquée avec succès!'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def add_conclusion_view(request, pk):
    """
    Vue pour ajouter une conclusion à l'audit (pour le reviewer)
    """
    # Vérifier que l'audit existe et que l'utilisateur est le reviewer
    try:
        audit = AcceptationAudit.objects.get(pk=pk)
    except AcceptationAudit.DoesNotExist:
        messages.error(request, 'Cet audit n\'existe pas.')
        return redirect('core:dashboard')
    
    # Vérifier les permissions : l'utilisateur doit être le reviewer ET l'audit doit être publié ET pas encore révisé
    is_reviewer = audit.is_published and audit.reviewed_by == request.user
    if not is_reviewer:
        messages.error(request, 'Vous n\'avez pas l\'autorisation d\'ajouter une conclusion à cet audit.')
        return redirect('core:dashboard')
    
    if audit.is_reviewed:
        messages.warning(request, 'Cet audit a déjà été révisé.')
        return redirect('core:audit_detail', pk=audit.pk)
    
    # Récupérer les profils senior du département Audit
    senior_profiles = Profile.objects.filter(departement='audit', status='senior', deleted=False).select_related('user')
    
    if request.method == 'POST':
        form = AuditConclusionForm(request.POST, instance=audit, senior_profiles=senior_profiles)
        if form.is_valid():
            # Mettre à jour les champs du formulaire
            audit.accepte_mission = form.cleaned_data['accepte_mission']
            audit.conclusion_mission = form.cleaned_data['conclusion_mission']
            audit.global_risk = form.cleaned_data['global_risk']
            audit.diligence_risk = form.cleaned_data['diligence_risk']
            
            # Mettre à jour signed_by, is_reviewed, reviewed_at
            signed_by_id = int(form.cleaned_data['signed_by_id'])
            try:
                signed_profile = Profile.objects.get(pk=signed_by_id, departement='audit', status='senior', deleted=False)
                audit.signed_by = signed_profile.user
            except Profile.DoesNotExist:
                messages.error(request, 'Le profil sélectionné n\'existe pas ou n\'appartient pas au département Audit avec le statut Senior.')
                return redirect('core:add_conclusion', pk=audit.pk)
            
            audit.is_reviewed = True
            audit.reviewed_at = timezone.now().date()
            audit.save()
            
            # Construire l'URL absolue pour le lien vers la page de détail de l'audit
            audit_detail_url = request.build_absolute_uri(reverse('core:audit_detail', kwargs={'pk': audit.pk}))
            
            # Préparer et envoyer l'email au signataire
            message = form.cleaned_data.get('message', '').strip()
            recipient_email = signed_profile.user.email
            subject = f'Audit révisé - {audit.reference}'
            
            email_body = f"""
Bonjour {signed_profile.user.get_full_name() or signed_profile.user.username},

Une mission d'acceptation a été revue et nécessite votre signature :

Référence : {audit.reference}
Client : {audit.client}
Exercice : {audit.exercice}
Créé par : {audit.done_by.get_full_name() or audit.done_by.username}
Révisé par : {audit.reviewed_by.get_full_name() or audit.reviewed_by.username}
Date de révision : {audit.reviewed_at.strftime('%d/%m/%Y')}
Décision : {'Accepter la mission' if audit.accepte_mission == 'yes' else 'Refuser la mission'}
Risque global : {audit.get_global_risk_display()}
Vigilance de la diligence : {audit.get_diligence_risk_display()}

{f'Message :\n{message}' if message else ''}

Veuillez consulter les détails du formulaire en cliquant sur le lien suivant :
{audit_detail_url}

Cordialement,
MOORE SÉNÉGAL
"""
            
            # Envoyer l'email au signataire (en mode console pour le développement)
            email_sent_to_signer = False
            try:
                send_mail(
                    subject=subject,
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                email_sent_to_signer = True
            except Exception as e:
                # Même en cas d'erreur d'envoi d'email, on garde la conclusion
                messages.warning(request, f'Erreur lors de l\'envoi de l\'email au signataire: {str(e)}')
            
            # Envoyer un email de notification au créateur de l'audit (done_by)
            if audit.done_by and audit.done_by.email:
                creator_email = audit.done_by.email
                creator_subject = f'Audit révisé - {audit.reference}'
                
                creator_email_body = f"""
Bonjour {audit.done_by.get_full_name() or audit.done_by.username},

Votre mission d'acceptation a été révisée :

Référence : {audit.reference}
Client : {audit.client}
Exercice : {audit.exercice}
Révisé par : {audit.reviewed_by.get_full_name() or audit.reviewed_by.username}
Date de révision : {audit.reviewed_at.strftime('%d/%m/%Y')}
Décision : {'Accepter la mission' if audit.accepte_mission == 'yes' else 'Refuser la mission'}
Risque global : {audit.get_global_risk_display()}
Vigilance de la diligence : {audit.get_diligence_risk_display()}

{f'Message du réviseur :\n{message}' if message else ''}

Le formulaire a été transmis à {signed_profile.user.get_full_name() or signed_profile.user.username} pour signature.

Vous pouvez consulter les détails du formulaire en cliquant sur le lien suivant :
{audit_detail_url}

Cordialement,
MOORE SÉNÉGAL
"""
                
                try:
                    send_mail(
                        subject=creator_subject,
                        message=creator_email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[creator_email],
                        fail_silently=False,
                    )
                except Exception as e:
                    messages.warning(request, f'Erreur lors de l\'envoi de l\'email au créateur: {str(e)}')
            
            if email_sent_to_signer:
                messages.success(request, f'Conclusion envoyée avec succès! Des notifications ont été envoyées à {signed_profile.user.get_full_name() or signed_profile.user.username} et au créateur de l\'audit.')
            else:
                messages.info(request, 'Conclusion enregistrée. Des erreurs sont survenues lors de l\'envoi des notifications.')
            
            return redirect('core:audit_detail', pk=audit.pk)
    else:
        form = AuditConclusionForm(instance=audit, senior_profiles=senior_profiles)
    
    context = {
        'form': form,
        'audit': audit,
        'senior_profiles': senior_profiles,
    }
    return render(request, 'core/add_conclusion.html', context)
