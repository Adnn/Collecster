from django.db import models

class Container(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return "Container: " + self.name


class Element(models.Model):
    name = models.CharField(max_length=60)
    container = models.ForeignKey(Container) 

    def __str__(self):
        return "Element: " + self.name
