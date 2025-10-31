from django.db import models
from django_countries.fields import CountryField
from client.models import Client
from account.models import Profile, Departement
from django.contrib.auth.models import User
import os
import time
import random
from uuid import uuid4


def audit_signature_path(instance, filename):
    """Fonction pour générer le chemin de stockage de la signature senior"""
    upload_to = 'audit_signatures'
    ext = filename.split('.')[-1]
    current_time = int(time.time())
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr = ''.join((random.choice(chars)) for x in range(26))
    # get filename
    if instance.pk:
        filename = 'audit_{}{}{}.{}'.format(
            instance.pk, randomstr, current_time, ext)
    else:
        # set filename as random string
        filename = '{}{}{}.{}'.format(
            uuid4().hex, randomstr, current_time, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class AcceptationAudit(models.Model):
    EIP_OPTION = [
        ('', '--'),
        ('yes', 'Oui'),
        ('no', 'Non'),
    ]
    COCA_OPTION = [
        ('', '--'),
        ('yes', 'Oui'),
        ('no', 'Non'),
    ]
    COMPONENT_AUDIT_OPTION = [
        ('', '--'),
        ('yes', 'Oui'),
        ('no', 'Non'),
    ]
    INDEPENDENT_REVIEW_OPTION = [
        ('', '--'),
        ('yes', 'Oui'),
        ('no', 'Non'),
    ]
    RESPONSE_OPTION = [
        ('', '--'),
        ('yes', 'Oui'),
        ('no', 'Non'),
        ('not_applicable', 'N/A'),
    ]
    ACCEPT_MISSION_OPTION = [
        ('', '--'),
        ('yes', 'Accepter la mission'),
        ('no', 'Refuser la mission'),
    ]
    GLOBAL_RISK_OPTION = [
        ('', '--'),
        ('low', 'Risque faible'),
        ('medium', 'Risque modéré'),
        ('high', 'Risque élevé'),
    ]
    DILLIGENCE_RISK_OPTION = [
        ('', '--'),
        ('normal', 'Vigilance normale'),
        ('enhanced', 'Vigilance renforcée'),
    ]

    # Step 1
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="missions_audit_client", verbose_name="Client")
    reference = models.CharField(max_length=100, verbose_name="Référence")
    # Liste d'années autorisées pour l'exercice
    YEARS_CHOICES = [(str(y), str(y)) for y in range(2015, 2036)]
    exercice = models.CharField(max_length=4, choices=YEARS_CHOICES, verbose_name="Exercice")
    step_1 = models.BooleanField(default=False, verbose_name="Étape 1")
    
    done_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="missions_audit_done_by", verbose_name="Fait par")
    done_at = models.DateField(verbose_name="Le", null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="missions_audit_reviewed_by", verbose_name="Revu par")
    reviewed_at = models.DateField(verbose_name="Le (révision)", null=True, blank=True)
    signed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="missions_audit_signed_by", verbose_name="Signé par")
    signed_at = models.DateField(verbose_name="Le (signature)", null=True, blank=True)
    
    # Step 2
    company_name = models.CharField(max_length=255, verbose_name="Raison sociale")
    closing_date = models.DateField(verbose_name="Date de clôture", blank=True, null=True)
    legal_form = models.CharField(max_length=255, verbose_name="Forme juridique (de l'entité)")
    group_name = models.CharField(max_length=255, verbose_name="Nom du groupe")
    is_eip = models.CharField(max_length=10, choices=EIP_OPTION, verbose_name="EIP (O/N)")
    stock_exchange = models.CharField(max_length=255, verbose_name="Si entité cotée, bourse(s) de cotation", blank=True, null=True)
    countries_operated = models.CharField(max_length=255, verbose_name="Pays dans lesquels opère l'entité")
    business_description = models.TextField(verbose_name="Décrire la nature des activités et la taille de l'entité (par exemple secteur d'activité, produits ou services, principaux clients, principaux fournisseurs)")
    start_year = models.CharField(max_length=10, verbose_name="Si l'entité a moins de cinq ans, indiquer l'année de démarrage de l'activité", blank=True, null=True)
    step_2 = models.BooleanField(default=False, verbose_name="Étape 2")

    # Step 3
    contact_origin = models.CharField(max_length=255, verbose_name="Origine du contact", blank=True)
    mission_nature = models.CharField(max_length=255, verbose_name="Nature de la mission", blank=True)
    has_cocac = models.CharField(max_length=10, choices=COCA_OPTION, verbose_name="S'agit -il d'un Co-CAC ? Si oui indiquer le nom du co-CAC")
    cocac_name = models.CharField(max_length=255, verbose_name="Nom du co-CAC (si applicable)", blank=True, null=True)
    is_component_audit = models.CharField(max_length=10, choices=COMPONENT_AUDIT_OPTION, verbose_name="S'agit-il de l'audit d'un composant ? Si oui nom de l'auditeur du groupe")
    component_audit_name = models.CharField(max_length=255, verbose_name="Nom du composant (si applicable)", blank=True, null=True)
    total_fees = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Honoraires totaux prévus (si possible)")
    has_independent_review = models.CharField(max_length=10, choices=INDEPENDENT_REVIEW_OPTION, verbose_name="Le dossier répond-il aux critères de la revue indépendante ? Si oui le(s)quel(s)")
    independent_review_name = models.CharField(max_length=255, verbose_name="Nom de la revue indépendante (si applicable)", blank=True, null=True)
    step_3 = models.BooleanField(default=False, verbose_name="Étape 3")

    # Step 4
    step_4 = models.BooleanField(default=False, verbose_name="Étape 4")

    # Step 5
    step_5 = models.BooleanField(default=False, verbose_name="Étape 5")

    # Step 6
    step_6 = models.BooleanField(default=False, verbose_name="Étape 6")

    # Champs de réponse numérotés de 1 à 82
    # Etape 7
    question_1 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Les honoraires envisagés représentent-ils une part significative des honoraires du signataire (honoraires égaux ou supérieurs à 15% du CA du signataire) ? Si oui indiquer ci-contre les mesures de sauvegarde prévues.")
    response_1 = models.TextField(verbose_name="Réponse 1", blank=True)
    question_2 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Nos honoraires sont-ils insuffisants pour nous permettre d'effectuer notre travail conformément aux normes ?")
    response_2 = models.TextField(verbose_name="Réponse 2", blank=True)
    question_3 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="A-t-on connaissance de liens financiers entre, d'une part, la personne ou l'entité contrôlée ou l'une des personnes qui la contrôle ou est contrôlée par elle et, d'autre part, le signataire ou un membre de sa famille ?")
    response_3 = models.TextField(verbose_name="Réponse 3", blank=True)
    question_4 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Le cabinet ou ses associés ont-ils obtenu/accordé un emprunt, des avances de fonds ou des garanties?")
    response_4 = models.TextField(verbose_name="Réponse 4", blank=True)
    question_5 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Existe-t-il une participation financière détenue chez le client ou une entité qui la controle ou qui est contrôlée par elle par :  ")
    response_5 = models.TextField(verbose_name="Réponse 5", blank=True)
    question_6 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="a. Un associé du cabinet ou un membre de sa famille proche ?")
    response_6 = models.TextField(verbose_name="Réponse 6", blank=True)
    question_7 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="b. Le cabinet")
    response_7 = models.TextField(verbose_name="Réponse 7", blank=True)
    question_8 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="c. Un membre du réseau ?")
    response_8 = models.TextField(verbose_name="Réponse 8", blank=True)
    question_9 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="d. Un membre de l'équipe de la mission ?")
    response_9 = models.TextField(verbose_name="Réponse 9", blank=True)
    question_10 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="L'acceptation de cette mission peut-elle compromettre notre relation avec nos clients existants ? Par exemple, un des concurrents de ce client est-il client chez nous et ceci menace-t-il notre indépendance ? Si OUI, préciser ci-contre si vous obtenu le consentement écrit des deux clients.")
    response_10 = models.TextField(verbose_name="Réponse 10", blank=True)
    question_11 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Existe-t-il des relations d'affaires avec le client ou sa direction pouvant constituer une menace pour l'indépendance?")
    response_11 = models.TextField(verbose_name="Réponse 11", blank=True)
    question_12 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="A-t-on connaissance de liens familiaux entre, d'une part, une personne occupant une fonction sensible  au sein de l'entité contrôlée et, d'autre part, le commissaire aux comptes, l'un des membres de l'équipe de contrôle, l'un des membres de la direction du cabinet ou l'un des associés du cabinet ou leurs familles ?")
    response_12 = models.TextField(verbose_name="Réponse 12", blank=True)
    question_13 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="A-t-on connaissance de liens personnels autres que familiaux entre, d'une part, l'entité contrôlée ou une personne y occupant une fonction sensible et, d'autre part, le commissaire aux comptes ou l'un des membres de la direction du cabinet ?")
    response_13 = models.TextField(verbose_name="Réponse 13", blank=True)
    question_14 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Existe-t-il un litige opposant au client le cabinet, et susceptible d'affecter notre indépendance ?")
    response_14 = models.TextField(verbose_name="Réponse 14", blank=True)
    question_15 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="A-t-on procédé aux vérifications requises dans COPERNICUS ? Joindre les preuves ")
    response_15 = models.TextField(verbose_name="Réponse 15", blank=True)
    question_16 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Si l'entité ou l'une de ses parties liées disposent d'opérations à l'international et si/ou elle est cotée ou EIP a-t-on effectué network conflict checking ? Joindre les preuves")
    response_16 = models.TextField(verbose_name="Réponse 16", blank=True)
    question_17 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Après avoir pris connaissance des prestations de service rendues antérieurement par le cabinet ou par son réseau au client, ou à une entité contrôlée par celle-ci ou qui la contrôle, y a-t-il un risque d'auto révision pouvant en découler ?")
    response_17 = models.TextField(verbose_name="Réponse 17", blank=True)
    question_18 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="A-t-on procédé au domestic check ? Joindre les preuves")
    response_18 = models.TextField(verbose_name="Réponse 18", blank=True)
    question_19 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Le cabinet, les membres du réseau (notamment le réseau Moore) ont-ils réalisé en faveur du client ou des entités qui la contrôle ou qu'elle contrôle, des prestations incompatibles avec le mandat de CAC ?")
    response_19 = models.TextField(verbose_name="Réponse 19", blank=True)
    question_20 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Sommes-nous dans l'un des cas d'interdiction mentionnés dans les articles 698 à 700 de l'AUSCGIE ?")
    response_20 = models.TextField(verbose_name="Réponse 20", blank=True)
    question_21 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Sommes-nous convaincus qu'il n'y a pas d'autres objections éthiques sur la base desquelles le cabinet n'accepterait pas le client ?")
    response_21 = models.TextField(verbose_name="Réponse 21", blank=True)
    question_22 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Question 22", blank=True)
    response_22 = models.TextField(verbose_name="Réponse 22", blank=True)
    step_7 = models.BooleanField(default=False, verbose_name="Étape 7")
    
    # Etape 8
    question_23 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous obtenu l'original ou l'expédition ou la copie certifiée conforme de l'extrait du RCCM attestant : ")
    response_23 = models.TextField(verbose_name="Réponse 23", blank=True)
    question_24 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="a. La forme juridique ?")
    response_24 = models.TextField(verbose_name="Réponse 24", blank=True)
    question_25 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="b.	Le siège social ?")
    response_25 = models.TextField(verbose_name="Réponse 25", blank=True)
    question_26 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="c.	Les pouvoirs des personnes agissant au nom de la société ?")
    response_26 = models.TextField(verbose_name="Réponse 26", blank=True)
    question_27 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous obtenu les statuts à jour ?")
    response_27 = models.TextField(verbose_name="Réponse 27", blank=True)
    question_28 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Connaissons-nous avec certitude l'adresse du client ?")
    response_28 = models.TextField(verbose_name="Réponse 28", blank=True)
    question_29 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous personnellement rencontré le client (face à face) ?")
    response_29 = models.TextField(verbose_name="Réponse 29", blank=True)
    question_30 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous pu identifier les administrateurs au travers de la publication de leur nomination ainsi que des comptes annuels déposés ?")
    response_30 = models.TextField(verbose_name="Réponse 30", blank=True)
    question_31 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous une copie de la pièce d'identité des administrateurs, gérants et directeurs de la société (document original, en cours de validité, avec photo et adresse dont nous prenons nous même une copie) ?")
    response_31 = models.TextField(verbose_name="Réponse 31", blank=True)
    question_32 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous un document probant permettant de valider leur pouvoir d'engager la société ?")
    response_32 = models.TextField(verbose_name="Réponse 32", blank=True)
    question_33 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Connaissons-nous l'identité de l'ayant droit économique ?")
    response_33 = models.TextField(verbose_name="Réponse 33", blank=True)
    question_34 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="S'il s'agit d'une personne morale, avons-nous obtenu les documents d'identification énoncés au point 15 ci-dessus ?")
    response_34 = models.TextField(verbose_name="Réponse 34", blank=True)
    question_35 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="S'il s'agit d'une personne physique, avons-nous obtenu une pièce d'identité, en cours de validité, avec photo, et adresse (original dont nous prenons nous même copie) ?")
    response_35 = models.TextField(verbose_name="Réponse 35", blank=True)
    question_36 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous obtenu les justificatifs d'adresse ?")
    response_36 = models.TextField(verbose_name="Réponse 36", blank=True)
    question_37 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous procédé à des vérifications complémentaires via des moteurs de recherche ou d'autres sources externes sur l'entité et ses dirigeants clés ?")
    response_37 = models.TextField(verbose_name="Réponse 37", blank=True)
    question_38 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Le client est-il une PPE nationale ou étrangère ? (Si oui, Application des procédures spécifiques prévues par l'article 54 de la loi LBCFT).")
    response_38 = models.TextField(verbose_name="Réponse 38", blank=True)
    question_39 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Dans le cas d'une PPE étrangère avons-nous pu établir l'origine du patrimoine et l'origine des fonds impliqués dans la relation d'affaires ou la transaction ?")
    response_39 = models.TextField(verbose_name="Réponse 39", blank=True)
    step_8 = models.BooleanField(default=False, verbose_name="Étape 8")
    
    # Etape 9
    question_40 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="A-t-on procédé au background check tel qu'il est prévu dans le manuel ISQM du cabinet ? (Joindre les preuves)")
    response_40 = models.TextField(verbose_name="Réponse 40", blank=True)
    question_41 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Des doutes ont-ils été soulevés concernant l'intégrité de l'entité, ses propriétaires, administrateurs, dirigeants ?")
    response_41 = models.TextField(verbose_name="Réponse 41", blank=True)
    question_42 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="La réputation et l'image de l'entreprise et de l'organe de gestion sont-elles contestables ?")
    response_42 = models.TextField(verbose_name="Réponse 42", blank=True)
    question_43 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Les recherches effectuées et les informations obtenues sur l'historique professionnel pertinent des administrateurs/gérants actuels sont-elles sources de préoccupation ?")
    response_43 = models.TextField(verbose_name="Réponse 43", blank=True)
    question_44 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="La nature des activités du client, en ce compris la gestion d'entreprise, est-elle propice aux risques en matière d'intégrité ?")
    response_44 = models.TextField(verbose_name="Réponse 44", blank=True)
    question_45 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Dispose-t-on d'informations portant à croire que le client participe au blanchiment d'argent, au financement du terrorisme, ou à d'autres activités criminelles, et notamment la provenance des fonds ?")
    response_45 = models.TextField(verbose_name="Réponse 45", blank=True)
    question_46 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous relevé des sources de préoccupation dans les documents d'identification obtenus ou en raison de leur non obtention ?")
    response_46 = models.TextField(verbose_name="Réponse 46", blank=True)
    step_9 = models.BooleanField(default=False, verbose_name="Étape 9")

    # Etape 10
    question_47 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Décrivez succinctement les activités et les clients les plus importants de la société : ceux-ci constituent-ils un risque spécifique ?")
    response_47 = models.TextField(verbose_name="Réponse 47", blank=True)
    question_48 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Le client intervient-il dans un secteur d'activité exposé à la fraude ou à des risques de blanchiment d'argent ou de financement du terrorisme ?")
    response_48 = models.TextField(verbose_name="Réponse 48", blank=True)
    question_49 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Image médiatique du dirigeant et/ou de l'entreprise est-elle susceptible de nuire à l'image du cabinet ?")
    response_49 = models.TextField(verbose_name="Réponse 49", blank=True)
    step_10 = models.BooleanField(default=False, verbose_name="Étape 10")

    # Etape 11
    question_50 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Si notre nomination intervient dans le cadre d'un non renouvellement, d'une démission ou d'un empêchement, avons-nous pris contact avec le confrère précédent ?")
    response_50 = models.TextField(verbose_name="Réponse 50", blank=True)
    question_51 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Les discussions avec le prédécesseur ont-elles révélé des risques sur les éléments suivants :")
    response_51 = models.TextField(verbose_name="Réponse 51", blank=True)
    question_52 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="(a) L'accès aux dossiers du client ;")
    response_52 = models.TextField(verbose_name="Réponse 52", blank=True)
    question_53 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="(b) Les honoraires impayés ;")
    response_53 = models.TextField(verbose_name="Réponse 53", blank=True)
    question_54 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="(c) Les divergences d'opinions ou différends ;")
    response_54 = models.TextField(verbose_name="Réponse 54", blank=True)
    question_55 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="(d) L'intégrité des dirigeants et du conseil ;")
    response_55 = models.TextField(verbose_name="Réponse 55", blank=True)
    question_56 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="(e) Les raisons du changement ;")
    response_56 = models.TextField(verbose_name="Réponse 56", blank=True)
    question_57 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="(f) Les exigences déraisonnables ou le manque de coopération ?")
    response_57 = models.TextField(verbose_name="Réponse 57", blank=True)
    question_58 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="(g) Le non-respect des lois et réglementations ?")
    response_58 = models.TextField(verbose_name="Réponse 58", blank=True)
    question_59 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="(h) Autres raisons pour lesquelles nous ne devrions pas accepter la mission.")
    response_59 = models.TextField(verbose_name="Réponse 59", blank=True)
    question_60 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Les procédures légales de démission ou révocation ont-elles été respectées ? ")
    response_60 = models.TextField(verbose_name="Réponse 60", blank=True)
    step_11 = models.BooleanField(default=False, verbose_name="Étape 11")

    # Etape 12
    question_61 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Existe-t-il des problèmes de continuité à signaler ou à anticiper ?")
    response_61 = models.TextField(verbose_name="Réponse 61", blank=True)
    question_62 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Les méthodes comptables utilisées dans le cadre de la préparation des états financiers sont-elles sources de préoccupation en termes d'adéquation et de permanence des méthodes ?")
    response_62 = models.TextField(verbose_name="Réponse 62", blank=True)
    question_63 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Des risques fiscaux, sociaux, juridiques sont-ils liés à l'activité de la société ?")
    response_63 = models.TextField(verbose_name="Réponse 63", blank=True)
    question_64 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="La direction n'est pas sensible aux recommandations ou n'a pas mis en place les recommandations de contrôle interne émises par les auditeurs internes et/ou externes.")
    response_64 = models.TextField(verbose_name="Réponse 64", blank=True)
    question_65 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Le client est-il soumis à une réglementation particulière ?")
    response_65 = models.TextField(verbose_name="Réponse 65", blank=True)
    question_66 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="La revue des rapports et dossiers des exercices précédents a-t-elle révélé ")
    response_66 = models.TextField(verbose_name="Réponse 66", blank=True)
    question_67 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="a.	Des réserves")
    response_67 = models.TextField(verbose_name="Réponse 67", blank=True)
    question_68 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="b.	D'autres anomalies significatives")
    response_68 = models.TextField(verbose_name="Réponse 68", blank=True)
    question_69 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="c.	Des problématiques comptables particulières ?")
    response_69 = models.TextField(verbose_name="Réponse 69", blank=True)
    question_70 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="La comptabilité semble-t-elle être mal tenue ou en retard ?")
    response_70 = models.TextField(verbose_name="Réponse 70", blank=True)
    question_71 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Organisation déficiente pouvant entraîner des limitations aux travaux d'audit ?")
    response_71 = models.TextField(verbose_name="Réponse 71", blank=True)
    question_72 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="La compétence ou l'expérience du personnel sont-elles un facteur de risques ?")
    response_72 = models.TextField(verbose_name="Réponse 72", blank=True)
    question_73 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Incertitude sur l'exhaustivité des transactions du fait de l'activité, de l'organisation et/ou du dirigeant")
    response_73 = models.TextField(verbose_name="Réponse 73", blank=True)
    question_74 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous identifié des facteurs de risque de fraude concernant l'entité ?")
    response_74 = models.TextField(verbose_name="Réponse 74", blank=True)
    question_75 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Si l'entité opère dans un secteur réglementé, avons-nous des difficultés pour obtenir les autorisations/agréments nécessaires ?")
    response_75 = models.TextField(verbose_name="Réponse 75", blank=True)
    question_76 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="En cas de CO-CAC, avons-nous des doutes sur la capacité du COCAC à remplir ses obligations dans le respect des normes professionnelles ?")
    response_76 = models.TextField(verbose_name="Réponse 76", blank=True)
    question_77 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Dans le cas de l'audit du groupe, notre Intervention est-elle limitée à certaines sociétés du groupe ?")
    response_77 = models.TextField(verbose_name="Réponse 77", blank=True)
    step_12 = models.BooleanField(default=False, verbose_name="Étape 12")

    # Etape 13
    question_78 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Y -a-t-il un risque que la direction de l'entité impose une limitation de l'étendue de l'audit ?")
    response_78 = models.TextField(verbose_name="Réponse 78", blank=True)
    question_79 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Le client attend-il de nous des positions différentes de celles du prédécesseur ?")
    response_79 = models.TextField(verbose_name="Réponse 79", blank=True)
    question_80 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous un doute sur notre capacité à réaliser la mission dans le délai défini ? ")
    response_80 = models.TextField(verbose_name="Réponse 80", blank=True)
    question_81 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Avons-nous un doute sur notre capacité à mobiliser le personnel en nombre suffisant disposant des compétences et des connaissances requises pour effectuer la mission ?")
    response_81 = models.TextField(verbose_name="Réponse 81", blank=True)
    question_82 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Le cas échéant, avons-nous un doute sur la disponibilité, la compétence et la réputation de l'expert devant intervenir sur la mission ?")
    response_82 = models.TextField(verbose_name="Réponse 82", blank=True)
    question_83 = models.CharField(max_length=20, choices=RESPONSE_OPTION, default='', verbose_name="Le cas échéant, rencontrons-nous des difficultés pour identifier un réviseur indépendant ayant les compétences et la disponibilité requises pour remplir le rôle ?")
    response_83 = models.TextField(verbose_name="Réponse 83", blank=True)
    step_13 = models.BooleanField(default=False, verbose_name="Étape 13")
    
    is_published = models.BooleanField(default=False, verbose_name="Audit envoyé")
    date_published = models.DateTimeField(verbose_name="Date d'envoi", null=True, blank=True)
    published_view_date = models.DateTimeField(verbose_name="Date de création vue", null=True, blank=True)

    accepte_mission = models.CharField(max_length=20, choices=ACCEPT_MISSION_OPTION, default='', verbose_name="Accepté", null=True, blank=True)
    conclusion_mission = models.TextField(verbose_name="Conclusion de la mission", null=True, blank=True)
    global_risk = models.CharField(max_length=20, choices=GLOBAL_RISK_OPTION, default='', verbose_name="Risque global", null=True, blank=True)
    diligence_risk = models.CharField(max_length=20, choices=DILLIGENCE_RISK_OPTION, default='', verbose_name="Vigilance de la diligence", null=True, blank=True)
    date_reviewed = models.DateTimeField(verbose_name="Date de révision", null=True, blank=True)
    is_reviewed = models.BooleanField(default=False, verbose_name="Revu")


    is_signed = models.BooleanField(default=False, verbose_name="Signé")
    signed_view_date = models.DateTimeField(verbose_name="Date de archivage vue", null=True, blank=True)
    senior_signature = models.ImageField(upload_to=audit_signature_path, blank=True, null=True, verbose_name="Signature senior")

    date_added = models.DateTimeField(auto_now_add=True,verbose_name="Date de création")
    date_updated = models.DateTimeField(auto_now=True,verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Acceptation d'audit"
        verbose_name_plural = "Acceptations d'audit"
        ordering = ["-date_added"]

    def get_yes_responses_count(self):
        """Compter les réponses 'Oui'"""
        count = 0
        for i in range(1, 84):
            field_name = f'question_{i}'
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if value == 'yes':
                    count += 1
        return count

    def get_no_responses_count(self):
        """Compter les réponses 'Non'"""
        count = 0
        for i in range(1, 84):
            field_name = f'question_{i}'
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if value == 'no':
                    count += 1
        return count

    def get_unanswered_count(self):
        """Compter les questions non renseignées"""
        count = 0
        for i in range(1, 84):
            field_name = f'question_{i}'
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if not value or value == '':
                    count += 1
        return count

    def __str__(self):
        return f"Acceptation Audit - {self.reference} ({self.client})"


class Sharehol(models.Model):
    acceptation_audit = models.ForeignKey(AcceptationAudit, on_delete=models.CASCADE, related_name="acceptation_audit_shareholder", verbose_name="Acceptation/Audit")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="added_shareholders", verbose_name="Ajouté par")
    identity = models.CharField(max_length=255, verbose_name="Identité")
    quantity_held = models.IntegerField(verbose_name="Quantité détenue")
    percentage_held = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="% détenu")
    quantity_vote = models.IntegerField(verbose_name="Quantité de vote")
    percentage_vote = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="% de vote")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    deleted = models.BooleanField(default=False, verbose_name="Supprimé")

    class Meta:
        verbose_name = "Actionnaire"
        verbose_name_plural = "Actionnaires"
        ordering = ["-date_added"]

    def __str__(self):
        return f"{self.identity} - {self.percentage_held}%"


class Branche(models.Model):
    acceptation_audit = models.ForeignKey(AcceptationAudit, on_delete=models.CASCADE, related_name="acceptation_audit_branche", verbose_name="Acceptation/Maintenance")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="added_branches", verbose_name="Ajouté par")
    identity = models.CharField(max_length=255, verbose_name="Identité")
    nationality = CountryField(verbose_name="Nationalité", blank=True, null=True)
    cac_auditor = models.PositiveIntegerField(verbose_name="CAC/Auditeur")
    ownership_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="% de détention")
    control_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="% de contrôle")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    deleted = models.BooleanField(default=False, verbose_name="Supprimé")

    class Meta:
        verbose_name = "Branche"
        verbose_name_plural = "Branches"
        ordering = ["-date_added"]

    def __str__(self):
        return f"{self.identity} - {self.ownership_percentage}%"


class Manager(models.Model):
    acceptation_audit = models.ForeignKey(AcceptationAudit, on_delete=models.CASCADE, related_name="acceptation_audit_manager", verbose_name="Acceptation/Maintenance")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="added_managers", verbose_name="Ajouté par")
    name = models.CharField(max_length=255, verbose_name="Nom")
    position = models.CharField(max_length=255, verbose_name="Poste")
    experience = models.CharField(max_length=255, verbose_name="Expérience")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    deleted = models.BooleanField(default=False, verbose_name="Supprimé")

    class Meta:
        verbose_name = "Manager"
        verbose_name_plural = "Managers"
        ordering = ["-date_added"]

    def __str__(self):
        return f"{self.name} - {self.position}"