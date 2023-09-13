from django.core.management.base import BaseCommand
from Directory.models import Gang, Character, Streamer, CharacterGangLink
from bs4 import BeautifulSoup as BS
import requests
import re
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    help = 'Updates the database with gang information via web scraping'

    member_words = ['member','og','mdma','leader','hangaround','associate','shinobi','full','prospect','shotcaller','blooded','prime minister',
                'vice prime minister','command','captain','king','enforcer','goon','g 1','g 2','g 3','lord','boss','president','sergeant',
                'chaplain','nomad','soldier','elder','treasurer','secretary','quartermaster','veteran','jefe','capitain','soldado',
                'ambassador','milf','scrapling','naked','council','founder','gangster','baby','huntsman','curator','sgt','oracle',
                'patched','sicario','oyabun','wakagashira','shateigashira','hashira','shingiin','adobaiza','komon','isha','kumi','mikomi','butler',
                'mechanic','sheriff','corporal','deputy','cadet','lieutenant','chief','officer','trooper','warden','ranger','doctor','mayor',
                'justice','judge','clerk','commissioner','paramedic','emt','trainee','supervisor','detective','director','attorney','admin',
                'attending','therapist','resident','intern','nurse']
        
    excluded_member_words = ['honourary','honorary','retired','inactive','branch']

    twitch_link_words = ['played','twitch'] 

    anon_no = 0
    

    def handle(self, *args, **kwargs):

        active_gov = [("PBSO", "/wiki/Paleto_Bay_Sheriff%27s_Office"),("SDSO", "/wiki/Senora_Desert_Sheriff%27s_Office"),("LSPD", "/wiki/Los_Santos_Police_Department"),
                          ("SASP", "/wiki/San_Andreas_State_Police"),("SASPR", "/wiki/San_Andreas_State_Park_Rangers"),("DOC", "/wiki/Department_of_Corrections"),
                          ("DOJ", "/wiki/Department_of_Justice"),("EMS", "/wiki/Emergency_Medical_Services"),("MCU", "/wiki/Major_Crimes_Unit"),("LSMG", "/wiki/Los_Santos_Medical_Group"),
                          ("HSPU", "/wiki/High_Speed_Pursuit_Unit")]

        GANG_DIR_URL = 'https://nopixel.fandom.com/wiki/Category:Gangs'
        GANG_DIR_URL_2 = 'https://nopixel.fandom.com/wiki/Category:Gangs?from=Seaside'
        RACING_DIR_URL = 'https://nopixel.fandom.com/wiki/Category:Racing_Crew'

        logger.info('Starting scraping gang information')
        
        gangs_unref = self.find_each_group_from_directory(GANG_DIR_URL)
        gangs_unref_p2 = self.find_each_group_from_directory(GANG_DIR_URL_2)
        racing_unref = self.find_each_group_from_directory(RACING_DIR_URL)   

        groups_unref = gangs_unref + gangs_unref_p2 + racing_unref
        group_names = []
        group_links = []


        for line in groups_unref:

            item_title = line.get('title')

            if ((not 'Template' in item_title) and ( not 'Category' in item_title) and (not '2.0' in item_title) and (not 'members' in item_title.lower()) and ('/' not in item_title) and (not item_title in group_names)):

                group_names.append(item_title)
                group_links.append(self.sanitize_wiki_link(line.get('href')))

        for dep in active_gov:

            group_names.append(dep[0])
            group_links.append(self.sanitize_wiki_link(dep[1]))

        group_quantity = len(group_names)

        Gang.objects.all().delete()
        Streamer.objects.all().delete()
        Character.objects.all().delete()
        CharacterGangLink.objects.all().delete()

        for i in range(group_quantity):
            Gang.objects.create(name=group_names[i], link=group_links[i], people_live = 0, people_on_gta = 0)

        all_gangs = Gang.objects.values('name', 'link')

        for gang in all_gangs:

            gang_name = gang['name']
            gang_link = gang['link']
            members_list = self.url_to_members(gang_link)

            for character_tuple in members_list:
            
                gang = Gang.objects.get(name = gang_name)
                gang_id = gang.id
                
                streamer_title = self.get_streamer_name_from_link(character_tuple[3])

                streamer, created = Streamer.objects.get_or_create(
                    streamer_name = streamer_title,
                    defaults={'streamer_is_live': 0, 'streamer_on_gta': 0, 'streamer_link': character_tuple[3]})
                
                streamer_id = streamer.id

                character, created = Character.objects.get_or_create(
                character_link=character_tuple[2],
                defaults={
                    'character_name': character_tuple[0],
                    'character_streamer_id': streamer_id}
                )

                character_id = character.id

                CharacterGangLink.objects.create(
                    member_character_id = character_id,
                    member_gang_id = gang_id,
                    member_role = character_tuple[1]
                )           
            
            logger.info(f"Processing gang: {gang_name}")

        distinct_gang_ids = CharacterGangLink.objects.values_list('member_gang__id', flat=True).distinct()
        Gang.objects.exclude(id__in=distinct_gang_ids).delete()

        logger.info('Successfully updated gang information')

    
    def sanitize_wiki_link(self, url):

        if 'http' in url:
            return url
        else:
            return 'https://nopixel.fandom.com' + url
        
    
    def get_html(self, url):

        page = requests.get(url)
        soup = BS(page.content, 'html.parser')

        return soup
    

    def clean_role(self, role):

        cleaned_role = ''
        index = 0

        for char in role:

            if not char.isnumeric() or index < 3: cleaned_role += char
            index += 1

        return cleaned_role.strip().lower()
    

    def get_twitch_from_url(self, url):

        if 'wiki' in url:
            html = self.get_html(url)
        else:
            return ''

        try:
            aside = html.find_all('aside')[0]
        except IndexError:
            print(f"Failed to process URL: {url}")
            return ''

        h3s = aside.find_all('h3', string=lambda text: any(word in (text or '').lower() for word in self.twitch_link_words))

        for h3 in h3s:

            h3parent_div = h3.find_parent('div')
            h3a_tag = h3parent_div.find('a')

            if h3a_tag:

                if ('twitch' in h3a_tag['href']):
                    return h3a_tag['href']
                
                elif ('kick' in h3a_tag['href']):     #recursion is too slow in python
                    return h3a_tag['href']
            
                elif ('wiki' in h3a_tag['href']):

                    return self.get_twitch_from_url(self.sanitize_wiki_link(h3a_tag['href']))
        
        pa_tag = None

        for tag in html.find_all(string=re.compile(r"played by", re.I)):

            next_tag = tag.find_next()

            if next_tag and next_tag.name == 'a':
                pa_tag = next_tag

        if pa_tag:

                if ('twitch' in pa_tag['href']):
                    return pa_tag['href']
                
                elif ('kick' in pa_tag['href']):     #recursion is too slow in python
                    return pa_tag['href']
            
                elif ('wiki' in pa_tag['href'] and not 'wikia' in pa_tag['href']):

                    return self.get_twitch_from_url(self.sanitize_wiki_link(pa_tag['href']))
        
        return ''
    

    def get_members_from_html(self, html):

        members = []
        members_set = set() #avoiding duplicate entries

        aside = html.find_all('aside')[0]

        h3s = aside.find_all('h3', string=lambda text: any(word in (text or '').lower() for word in self.member_words) and not any(excluded_word in (text or '').lower() for excluded_word in self.excluded_member_words)) #(text or '') is essential else it throws a fit at NoneTypes
        
        for line in h3s:

            parent_div = line.find_parent('div')
            member_name_tag = parent_div.find('a')
            if (member_name_tag and (member_name_tag.text not in members_set)):
                
                link = self.sanitize_wiki_link(member_name_tag['href'])
                
                members.append((member_name_tag.text, self.clean_role(line.text), link, self.get_twitch_from_url(link), self.twitch_link_words))
                members_set.add(member_name_tag.text)   #need to implement a fix for when there are several people in one box-- the GSF problem!
        
        return members
    

    def url_to_members(self, url):

        html = self.get_html(url)
        member_list = self.get_members_from_html(html)

        return member_list
    

    def find_each_group_from_directory(self, url):

        page = requests.get(url)
        soup = BS(page.content, 'html.parser')
        
        return soup.find_all(class_ = "category-page__member-link")
    

    def get_streamer_name_from_link(self, url):
        
        if url:
            return (url.rstrip('/').split('/')[-1]).lower()
        else:
            self.anon_no += 1
            return 'anon' + str(self.anon_no)


    def sanitize(self, name):

        cleanname = ''
        for char in name:
            if char == ' ':
                cleanname += '_'
            elif ((not char == ' ') and char.isalnum()):
                cleanname += char

        return cleanname