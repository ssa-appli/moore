from django import forms
from django.forms import inlineformset_factory
from .models import AcceptationAudit, Sharehol, Branche, Manager
from client.models import Client
from django.contrib.auth.models import User
from django_countries.widgets import CountrySelectWidget


class AcceptationAuditForm(forms.ModelForm):
    """
    Formulaire principal pour AcceptationAudit
    """
    class Meta:
        model = AcceptationAudit
        fields = [
            'client', 'reference', 'exercice', 'done_by', 'done_at',
            'reviewed_by', 'reviewed_at', 'company_name', 'closing_date',
            'legal_form', 'group_name', 'is_eip', 'stock_exchange',
            'countries_operated', 'business_description', 'start_year',
            'contact_origin', 'mission_nature', 'has_cocac', 'cocac_name',
            'is_component_audit', 'component_audit_name', 'total_fees',
            'has_independent_review', 'independent_review_name',
            # Questions 1-82
            'question_1', 'response_1', 'question_2', 'response_2',
            'question_3', 'response_3', 'question_4', 'response_4',
            'question_5', 'response_5', 'question_6', 'response_6',
            'question_7', 'response_7', 'question_8', 'response_8',
            'question_9', 'response_9', 'question_10', 'response_10',
            'question_11', 'response_11', 'question_12', 'response_12',
            'question_13', 'response_13', 'question_14', 'response_14',
            'question_15', 'response_15', 'question_16', 'response_16',
            'question_17', 'response_17', 'question_18', 'response_18',
            'question_19', 'response_19', 'question_20', 'response_20',
            'question_21', 'response_21', 'question_22', 'response_22',
            'question_23', 'response_23', 'question_24', 'response_24',
            'question_25', 'response_25', 'question_26', 'response_26',
            'question_27', 'response_27', 'question_28', 'response_28',
            'question_29', 'response_29', 'question_30', 'response_30',
            'question_31', 'response_31', 'question_32', 'response_32',
            'question_33', 'response_33', 'question_34', 'response_34',
            'question_35', 'response_35', 'question_36', 'response_36',
            'question_37', 'response_37', 'question_38', 'response_38',
            'question_39', 'response_39', 'question_40', 'response_40',
            'question_41', 'response_41', 'question_42', 'response_42',
            'question_43', 'response_43', 'question_44', 'response_44',
            'question_45', 'response_45', 'question_46', 'response_46',
            'question_47', 'response_47', 'question_48', 'response_48',
            'question_49', 'response_49', 'question_50', 'response_50',
            'question_51', 'response_51', 'question_52', 'response_52',
            'question_53', 'response_53', 'question_54', 'response_54',
            'question_55', 'response_55', 'question_56', 'response_56',
            'question_57', 'response_57', 'question_58', 'response_58',
            'question_59', 'response_59', 'question_60', 'response_60',
            'question_61', 'response_61', 'question_62', 'response_62',
            'question_63', 'response_63', 'question_64', 'response_64',
            'question_65', 'response_65', 'question_66', 'response_66',
            'question_67', 'response_67', 'question_68', 'response_68',
            'question_69', 'response_69', 'question_70', 'response_70',
            'question_71', 'response_71', 'question_72', 'response_72',
            'question_73', 'response_73', 'question_74', 'response_74',
            'question_75', 'response_75', 'question_76', 'response_76',
            'question_77', 'response_77', 'question_78', 'response_78',
            'question_79', 'response_79', 'question_80', 'response_80',
            'question_81', 'response_81', 'question_82', 'response_82',
            'question_83', 'response_83',
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'exercice': forms.Select(attrs={'class': 'form-control'}),
            'done_by': forms.Select(attrs={'class': 'form-control'}),
            'done_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reviewed_by': forms.Select(attrs={'class': 'form-control'}),
            'reviewed_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'closing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'legal_form': forms.TextInput(attrs={'class': 'form-control'}),
            'group_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_eip': forms.Select(attrs={'class': 'form-control'}),
            'stock_exchange': forms.TextInput(attrs={'class': 'form-control'}),
            'countries_operated': forms.TextInput(attrs={'class': 'form-control'}),
            'business_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_year': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_origin': forms.TextInput(attrs={'class': 'form-control'}),
            'mission_nature': forms.TextInput(attrs={'class': 'form-control'}),
            'has_cocac': forms.Select(attrs={'class': 'form-control'}),
            'cocac_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_component_audit': forms.Select(attrs={'class': 'form-control'}),
            'component_audit_name': forms.TextInput(attrs={'class': 'form-control'}),
            'total_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'has_independent_review': forms.Select(attrs={'class': 'form-control'}),
            'independent_review_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ajouter les widgets pour toutes les questions et réponses
        for i in range(1, 83):
            question_field = f'question_{i}'
            response_field = f'response_{i}'
            
            if question_field in self.fields:
                self.fields[question_field].widget.attrs.update({'class': 'form-control'})
            if response_field in self.fields:
                self.fields[response_field].widget.attrs.update({'class': 'form-control', 'rows': 2})


class ShareholForm(forms.ModelForm):
    """
    Formulaire pour Sharehol (Actionnaires)
    """
    class Meta:
        model = Sharehol
        fields = ['identity', 'quantity_held', 'percentage_held', 'quantity_vote', 'percentage_vote']
        widgets = {
            'identity': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity_held': forms.NumberInput(attrs={'class': 'form-control'}),
            'percentage_held': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_vote': forms.NumberInput(attrs={'class': 'form-control'}),
            'percentage_vote': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class BrancheForm(forms.ModelForm):
    """
    Formulaire pour Branche (Filiales)
    """
    class Meta:
        model = Branche
        fields = ['identity', 'nationality', 'cac_auditor', 'ownership_percentage', 'control_percentage']
        widgets = {
            'identity': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': CountrySelectWidget(attrs={'class': 'form-control'}),
            'cac_auditor': forms.TextInput(attrs={'class': 'form-control'}),
            'ownership_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'control_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class ManagerForm(forms.ModelForm):
    """
    Formulaire pour Manager (Dirigeants)
    """
    class Meta:
        model = Manager
        fields = ['name', 'position', 'experience']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.TextInput(attrs={'class': 'form-control'}),
        }


# FormSets pour permettre l'ajout de plusieurs lignes
ShareholFormSet = inlineformset_factory(
    AcceptationAudit, Sharehol, form=ShareholForm,
    extra=6, can_delete=True, fields=['identity', 'quantity_held', 'percentage_held', 'quantity_vote', 'percentage_vote']
)

BrancheFormSet = inlineformset_factory(
    AcceptationAudit, Branche, form=BrancheForm,
    extra=6, can_delete=True, fields=['identity', 'nationality', 'cac_auditor', 'ownership_percentage', 'control_percentage']
)

ManagerFormSet = inlineformset_factory(
    AcceptationAudit, Manager, form=ManagerForm,
    extra=6, can_delete=True, fields=['name', 'position', 'experience']
)


# Formulaires spécialisés pour chaque étape
class AuditStep1Form(forms.ModelForm):
    """
    Étape 1: Informations de base (client, reference, exercice)
    """
    class Meta:
        model = AcceptationAudit
        fields = ['client', 'reference', 'exercice']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'exercice': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['client', 'reference', 'exercice']:
            self.fields[field_name].required = True


class AuditStep2Form(forms.ModelForm):
    """
    Étape 2: Informations de l'entreprise
    """
    class Meta:
        model = AcceptationAudit
        fields = [
            'company_name', 'closing_date', 'legal_form', 'group_name', 
            'is_eip', 'stock_exchange', 'countries_operated', 
            'business_description', 'start_year'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'closing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'legal_form': forms.TextInput(attrs={'class': 'form-control'}),
            'group_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_eip': forms.Select(attrs={'class': 'form-control'}),
            'stock_exchange': forms.TextInput(attrs={'class': 'form-control',}),
            'countries_operated': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Séparer les pays par une virgule (,)'}),
            'business_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_year': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['company_name', 'closing_date', 'legal_form', 'group_name', 
                          'is_eip', 'stock_exchange', 'countries_operated', 
                          'business_description', 'start_year']:
            self.fields[field_name].required = True


class AuditStep3Form(forms.ModelForm):
    """
    Étape 3: Informations de la mission
    """
    class Meta:
        model = AcceptationAudit
        fields = [
            'contact_origin', 'mission_nature', 'has_cocac', 'cocac_name',
            'is_component_audit', 'component_audit_name', 'total_fees',
            'has_independent_review', 'independent_review_name'
        ]
        widgets = {
            'contact_origin': forms.TextInput(attrs={'class': 'form-control'}),
            'mission_nature': forms.TextInput(attrs={'class': 'form-control'}),
            'has_cocac': forms.Select(attrs={'class': 'form-control'}),
            'cocac_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_component_audit': forms.Select(attrs={'class': 'form-control'}),
            'component_audit_name': forms.TextInput(attrs={'class': 'form-control'}),
            'total_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'has_independent_review': forms.Select(attrs={'class': 'form-control'}),
            'independent_review_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Champs requis (hors champs optionnels précisés)
        for field_name in ['contact_origin', 'mission_nature', 'has_cocac',
                          'is_component_audit', 'total_fees', 'has_independent_review']:
            self.fields[field_name].required = True
        # Champs optionnels
        for optional_field in ['cocac_name', 'component_audit_name', 'independent_review_name']:
            if optional_field in self.fields:
                self.fields[optional_field].required = False


class AuditStep7Form(forms.ModelForm):
    """
    Étape 7: Questions 1-22
    """
    class Meta:
        model = AcceptationAudit
        fields = [
            'question_1', 'response_1', 'question_2', 'response_2',
            'question_3', 'response_3', 'question_4', 'response_4',
            'question_5', 'response_5', 'question_6', 'response_6',
            'question_7', 'response_7', 'question_8', 'response_8',
            'question_9', 'response_9', 'question_10', 'response_10',
            'question_11', 'response_11', 'question_12', 'response_12',
            'question_13', 'response_13', 'question_14', 'response_14',
            'question_15', 'response_15', 'question_16', 'response_16',
            'question_17', 'response_17', 'question_18', 'response_18',
            'question_19', 'response_19', 'question_20', 'response_20',
            'question_21', 'response_21', 'question_22', 'response_22',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 23):
            question_field = f'question_{i}'
            response_field = f'response_{i}'
            if question_field in self.fields:
                self.fields[question_field].widget.attrs.update({'class': 'form-control'})
                self.fields[question_field].required = True
            if response_field in self.fields:
                self.fields[response_field].widget.attrs.update({'class': 'form-control', 'rows': 2})


class AuditStep8Form(forms.ModelForm):
    """
    Étape 8: Questions 23-39
    """
    class Meta:
        model = AcceptationAudit
        fields = [
            'question_23', 'response_23', 'question_24', 'response_24',
            'question_25', 'response_25', 'question_26', 'response_26',
            'question_27', 'response_27', 'question_28', 'response_28',
            'question_29', 'response_29', 'question_30', 'response_30',
            'question_31', 'response_31', 'question_32', 'response_32',
            'question_33', 'response_33', 'question_34', 'response_34',
            'question_35', 'response_35', 'question_36', 'response_36',
            'question_37', 'response_37', 'question_38', 'response_38',
            'question_39', 'response_39',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(23, 40):
            question_field = f'question_{i}'
            response_field = f'response_{i}'
            if question_field in self.fields:
                self.fields[question_field].widget.attrs.update({'class': 'form-control'})
                self.fields[question_field].required = True
            if response_field in self.fields:
                self.fields[response_field].widget.attrs.update({'class': 'form-control', 'rows': 2})


class AuditStep9Form(forms.ModelForm):
    """
    Étape 9: Questions 40-46
    """
    class Meta:
        model = AcceptationAudit
        fields = [
            'question_40', 'response_40', 'question_41', 'response_41',
            'question_42', 'response_42', 'question_43', 'response_43',
            'question_44', 'response_44', 'question_45', 'response_45',
            'question_46', 'response_46',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(40, 47):
            question_field = f'question_{i}'
            response_field = f'response_{i}'
            if question_field in self.fields:
                self.fields[question_field].widget.attrs.update({'class': 'form-control'})
                self.fields[question_field].required = True
            if response_field in self.fields:
                self.fields[response_field].widget.attrs.update({'class': 'form-control', 'rows': 2})


class AuditStep10Form(forms.ModelForm):
    """
    Étape 10: Questions 47-49
    """
    class Meta:
        model = AcceptationAudit
        fields = [
            'question_47', 'response_47', 'question_48', 'response_48',
            'question_49', 'response_49',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(47, 50):
            question_field = f'question_{i}'
            response_field = f'response_{i}'
            if question_field in self.fields:
                self.fields[question_field].widget.attrs.update({'class': 'form-control'})
                self.fields[question_field].required = True
            if response_field in self.fields:
                self.fields[response_field].widget.attrs.update({'class': 'form-control', 'rows': 2})


class AuditStep11Form(forms.ModelForm):
    """
    Étape 11: Questions 50-60
    """
    class Meta:
        model = AcceptationAudit
        fields = [
            'question_50', 'response_50', 'question_51', 'response_51',
            'question_52', 'response_52', 'question_53', 'response_53',
            'question_54', 'response_54', 'question_55', 'response_55',
            'question_56', 'response_56', 'question_57', 'response_57',
            'question_58', 'response_58', 'question_59', 'response_59',
            'question_60', 'response_60',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(50, 61):
            question_field = f'question_{i}'
            response_field = f'response_{i}'
            if question_field in self.fields:
                self.fields[question_field].widget.attrs.update({'class': 'form-control'})
                self.fields[question_field].required = True
            if response_field in self.fields:
                self.fields[response_field].widget.attrs.update({'class': 'form-control', 'rows': 2})


class AuditStep12Form(forms.ModelForm):
    """
    Étape 12: Questions 61-77
    """
    class Meta:
        model = AcceptationAudit
        fields = [
            'question_61', 'response_61', 'question_62', 'response_62',
            'question_63', 'response_63', 'question_64', 'response_64',
            'question_65', 'response_65', 'question_66', 'response_66',
            'question_67', 'response_67', 'question_68', 'response_68',
            'question_69', 'response_69', 'question_70', 'response_70',
            'question_71', 'response_71', 'question_72', 'response_72',
            'question_73', 'response_73', 'question_74', 'response_74',
            'question_75', 'response_75', 'question_76', 'response_76',
            'question_77', 'response_77',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(61, 78):
            question_field = f'question_{i}'
            response_field = f'response_{i}'
            if question_field in self.fields:
                self.fields[question_field].widget.attrs.update({'class': 'form-control'})
                self.fields[question_field].required = True
            if response_field in self.fields:
                self.fields[response_field].widget.attrs.update({'class': 'form-control', 'rows': 2})


class AuditStep13Form(forms.ModelForm):
    """
    Étape 13: Questions 78-83
    """
    class Meta:
        model = AcceptationAudit
        fields = [
            'question_78', 'response_78', 'question_79', 'response_79',
            'question_80', 'response_80', 'question_81', 'response_81',
            'question_82', 'response_82', 'question_83', 'response_83',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(78, 84):
            question_field = f'question_{i}'
            response_field = f'response_{i}'
            if question_field in self.fields:
                self.fields[question_field].widget.attrs.update({'class': 'form-control'})
                self.fields[question_field].required = True
            if response_field in self.fields:
                self.fields[response_field].widget.attrs.update({'class': 'form-control', 'rows': 2})


class AuditStep15Form(forms.ModelForm):
    """
    Étape 15: Finalisation (pas de champs spécifiques, juste pour la cohérence)
    """
    class Meta:
        model = AcceptationAudit
        fields = []  # Pas de champs spécifiques pour cette étape


class AuditConclusionForm(forms.ModelForm):
    """
    Formulaire pour ajouter une conclusion à l'audit (pour le reviewer)
    """
    signed_by_id = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Signé par"
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ajoutez un message pour le signataire...'}),
        label="Message (optionnel)"
    )
    
    class Meta:
        model = AcceptationAudit
        fields = ['accepte_mission', 'conclusion_mission', 'global_risk', 'diligence_risk']
        widgets = {
            'accepte_mission': forms.Select(attrs={'class': 'form-control'}),
            'conclusion_mission': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'global_risk': forms.Select(attrs={'class': 'form-control'}),
            'diligence_risk': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        senior_profiles = kwargs.pop('senior_profiles', None)
        super().__init__(*args, **kwargs)
        # Rendre certains champs obligatoires
        self.fields['accepte_mission'].required = True
        self.fields['conclusion_mission'].required = True
        self.fields['global_risk'].required = True
        self.fields['diligence_risk'].required = True
        
        # Configurer le select pour signed_by_id avec les profils senior
        if senior_profiles:
            choices = [('', '-- Sélectionner un signataire --')]
            choices.extend([(str(p.pk), f"{p.user.get_full_name() or p.user.username}") for p in senior_profiles])
            self.fields['signed_by_id'].choices = choices
        else:
            self.fields['signed_by_id'].choices = [('', '-- Aucun signataire disponible --')]
