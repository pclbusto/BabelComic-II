import re
from urllib.request import urlopen

class comic_vine_info_issue_searcher():


    regex_search_serie = r"<td class=\"listing_publisher\"> <a href=\"/publisher/(\d*)/\">([^<]*)</a></td>[^<]*<td>" \
                         r" <a href=\"/series/(\d*)/\">([^<|]*)</a> (\[m\])*(\[b\])*</td>[^<]*<td> (\d*) </td>[^<]*<t" \
                         r"d style=\"text-align: right\"> (\d+) issues"
    regex_get_issue_number = r"Issue Number<\/th>[^<]*<td>[^<]*[^>]*[^<]*<span>(\d+)<\/span>"
    regex_get_issue_name = r"<th>Name<\/th>[^<]*<td>[^<][^>]*[^<]*<span>[^>]*>([^<]*)"
    regex_get_issue_description = r'<div class="wiki-item-display js-toc-content">[^<]*(.*)<\/div>[^<]*<div class="wiki-item-edit">[^<]*<div    id='
    regex_get_issue_cover_date= r'<th>Cover Date<\/th>[^<]*<td>[^<]*[^>]*[^<]*<span>([^<]*)'
    regex_get_issue_story_arc = r"4045-(\d*)"
    regex_get_issue_id_volume = r"4050-(\d*)"
    def __init__(self):
        pass

    def search_serie(self, url):
        html = urlopen(url).read().decode('utf-8')
        # print(html)
        numero_issue = '0'
        nombre_issue =''
        descripcion_issue = ''
        fecha_tapa_issue =''
        id_story_arc = []
        id_volumen_issue=''
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_number, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            numero_issue = match.group(1)
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_name, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            nombre_issue = match.group(1)
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_description, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            descripcion_issue = match.group(1)
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_cover_date, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            fecha_tapa_issue = match.group(1)
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_story_arc, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            id_story_arc.append(match.group(1))
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_id_volume, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            id_volumen_issue=match.group(1)



            # cadena = "Numero {numero} Nombre Editorial {Nombre_Editorial} Id Serie {Id_Serie} " \
            #          "Nombre Serie {Nombre_Serie}".format(Id_Editorial=match.group(1),Nombre_Editorial= match.group(2),
            #                                              Id_Serie=match.group(3), Nombre_Serie=match.group(4))
        print(numero_issue, nombre_issue, fecha_tapa_issue,id_story_arc, id_volumen_issue, descripcion_issue )

if __name__ == "__main__":
    comcis_org_searcher = comic_vine_info_issue_searcher()
    comcis_org_searcher.search_serie('https://comicvine.gamespot.com/green-lantern-39-agent-orange-part-1/4000-155207/')
    # comcis_org_searcher.search_serie('https://comicvine.gamespot.com/batman-708-judgment-on-gotham-part-one-one-good-ma/4000-265991/')
    # comcis_org_searcher.search_serie('https://comicvine.gamespot.com/batman-713-in-storybook-endings/4000-286879/')