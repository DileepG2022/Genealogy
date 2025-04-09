from django.db import models
from django.contrib.auth.models import User

class FamilyGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    staff_user = models.OneToOneField(User, on_delete=models.CASCADE)  # Each staff user is assigned to one family

    def __str__(self):
        return self.name

class Person(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    father = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children_father')
    mother = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children_mother')
    spouse = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='spouse_relation')
    # Allowing multiple family groups
    family_groups = models.ManyToManyField(FamilyGroup, related_name="members", blank=True)

    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # To track who added the person

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_family_tree(self):
        """Recursively fetches the family tree in a structured format."""
        tree = {
            'id': self.id,
            'name': f"{self.first_name} {self.last_name}",
            'children': []
        }
        children = Person.objects.filter(father=self) | Person.objects.filter(mother=self)
        for child in children:
            tree['children'].append(child.get_family_tree())
        return tree
