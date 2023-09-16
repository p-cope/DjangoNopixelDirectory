from django.contrib import admin

from .models import Gang, Streamer, Character, CharacterGangLink, GangData


admin.site.register(Gang)
admin.site.register(Streamer)
admin.site.register(Character)
admin.site.register(CharacterGangLink)
admin.site.register(GangData)
