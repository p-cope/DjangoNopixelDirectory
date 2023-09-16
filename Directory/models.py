from django.db import models
from django.utils.text import slugify


class Gang(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    link = models.URLField(unique=True)
    people_live = models.IntegerField()
    people_on_gta = models.IntegerField()

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Streamer(models.Model):
    streamer_name = models.CharField(max_length=255, unique=True)
    streamer_link = models.URLField()
    streamer_is_live = models.BooleanField()
    streamer_on_gta = models.BooleanField()
    streamer_title = models.CharField(max_length=255, blank=True, default="")
    streamer_viewcount = models.IntegerField(default=0)

    def __str__(self):
        return self.streamer_name
    

class Character(models.Model):
    character_name = models.CharField(max_length=255)
    character_link = models.URLField(unique=True)
    character_streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE)

    def __str__(self):
        return self.character_name
    

class CharacterGangLink(models.Model):
    member_character = models.ForeignKey(Character,on_delete=models.CASCADE)
    member_gang = models.ForeignKey(Gang,on_delete=models.CASCADE)
    member_role = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.member_character.character_name} in {self.member_gang.name}"
    
class GangData(models.Model):
    gang = models.ForeignKey(Gang, on_delete=models.CASCADE)
    people_live = models.IntegerField()
    people_on_gta = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.gang.name} at {self.timestamp}"