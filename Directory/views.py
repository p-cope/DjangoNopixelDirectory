from django.shortcuts import render, get_object_or_404
from .models import Gang, Streamer, Character, CharacterGangLink

active_group_names = ['PBSO','Hydra Gang','LSPD','The Mandem','Vendetta','SDSO','SASP','LSMG','Bondi Boys MC','Brouge Street Kingz','Diamond Dogs','Redline','HSPU','Angels',
                 'Chang Gang','HOA','EMS','MCU','Goon School','Yokai','DOC','DOJ','Ballas','Mayhem','R.U.S.T','The Families','VCB','Gulag Gang','Lost MC','Marabunta Grande',
                 'The Hidden','The Neon Tigers MC','Vagos','Venus Fly Traps','SASPR','Clowncil','Seaside']

def main_page(request):

    active_groups = Gang.objects.filter(name__in=active_group_names).order_by('-people_on_gta')
    inactive_groups = Gang.objects.exclude(name__in=active_group_names).order_by('-people_on_gta')
    return(render(request, 'main_page.html', {'active_groups' : active_groups, 'inactive_groups' : inactive_groups}))


def search(request):
    
    return(render(request, 'search.html'))


def gang_detail(request, gang_name):

    gang = get_object_or_404(Gang, slug=gang_name)
    character_links = gang.characterganglink_set.order_by("-member_character__character_streamer__streamer_on_gta").all()
    gangmembers = [link.member_character for link in character_links]
    return render(request, 'group_page.html', {'group': gang, 'gang_members': gangmembers})