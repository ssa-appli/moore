from django.db import models

# Client model
class Client(models.Model):
    contact_person = models.CharField(max_length=255, verbose_name="Personne de contact")
    email = models.EmailField(blank=True, null=True, verbose_name="Email contact")
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone contact")
    company_name = models.CharField(max_length=255, verbose_name="Nom de la société")
    raison_sociale = models.CharField(max_length=255, blank=True, null=True, verbose_name="Raison sociale")
    ninea = models.CharField(max_length=100, blank=True, null=True, verbose_name="NINEA")
    rccm = models.CharField(max_length=100, blank=True, null=True, verbose_name="RCCM")
    adresse = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse")
    deleted = models.BooleanField(default=False, verbose_name="Supprimé")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Date ajoutée")

    def __str__(self):
        return self.company_name