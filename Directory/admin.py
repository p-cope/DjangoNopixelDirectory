from django.contrib import admin

from .models import Gang, Streamer, Character, CharacterGangLink


admin.site.register(Gang)
admin.site.register(Streamer)
admin.site.register(Character)
admin.site.register(CharacterGangLink)
