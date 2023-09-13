from django.shortcuts import render, get_object_or_404
from .models import Gang, Streamer, Character, CharacterGangLink


def main_page(request):

    groups = Gang.objects.all().order_by('-people_on_gta')
    return(render(request, 'main_page.html', {'groups' : groups}))


def search(request):
    
    return(render(request, 'search.html'))


def gang_detail(request, gang_name):

    gang = get_object_or_404(Gang, slug=gang_name)
    character_links = gang.characterganglink_set.order_by("-member_character__character_streamer__streamer_on_gta").all()
    gangmembers = [link.member_character for link in character_links]
    return render(request, 'group_page.html', {'group': gang, 'gang_members': gangmembers})