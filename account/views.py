from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import base64
import os
from django.conf import settings
from .models import Profile

# Create your views here.

@login_required
def profile_view(request):
    """
    Vue pour afficher le profil de l'utilisateur connecté
    """
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None
    
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'account/profile.html', context)

def logout_view(request):
    """
    Vue pour déconnecter l'utilisateur
    """
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('core:login')

@login_required
def change_password_view(request):
    """
    Vue pour changer le mot de passe de l'utilisateur connecté
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour éviter la déconnexion
            messages.success(request, 'Votre mot de passe a été modifié avec succès.')
            return redirect('account:profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'account/change-password.html', context)

@login_required
def signature_view(request):
    """
    Vue pour afficher et gérer la signature de l'utilisateur
    """
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None
    
    context = {
        'profile': profile,
    }
    return render(request, 'account/signature.html', context)

@login_required
@require_POST
@csrf_exempt
def save_signature_view(request):
    """
    Vue pour sauvegarder la signature de l'utilisateur
    """
    try:
        signature_data = request.POST.get('signature')
        if not signature_data:
            return JsonResponse({'success': False, 'error': 'Aucune signature fournie'})
        
        # Décoder l'image base64
        if signature_data.startswith('data:image'):
            format_type = signature_data.split(';')[0].split('/')[1]
            image_data = signature_data.split(',')[1]
        else:
            return JsonResponse({'success': False, 'error': 'Format de signature invalide'})
        
        # Créer ou récupérer le profil
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # Créer le nom du fichier
        filename = f"signature_{request.user.id}.{format_type}"
        
        # Chemin de sauvegarde
        signature_path = os.path.join(settings.MEDIA_ROOT, 'signatures', filename)
        os.makedirs(os.path.dirname(signature_path), exist_ok=True)
        
        # Sauvegarder le fichier
        with open(signature_path, 'wb') as f:
            f.write(base64.b64decode(image_data))
        
        # Mettre à jour le profil
        profile.signature.name = f'signatures/{filename}'
        profile.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Signature sauvegardée avec succès',
            'signature_url': profile.signature.url
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
