import re
from urllib.request import urlopen
from Entidades.ComicBooks.ComicBookInfo import Comicbooks_Info
from datetime import date

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
    regex_get_issue_url_cover = r"(https://static.comicvine.com/uploads/scale_large[^\"]*)"
    def __init__(self):
        pass

    def search_serie(self, url):
        html = urlopen(url).read().decode('utf-8')
        # print(html)
        comicbook_info = Comicbooks_Info()
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_number, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.numero = match.group(1)
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_name, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.titulo = match.group(1)
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_description, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.resumen = match.group(1)
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_cover_date, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            fecha_tapa_issue = match.group(1)
            mes=0
            if fecha_tapa_issue.find("January")!=-1:
                mes = 1
            if fecha_tapa_issue.find("February")!=-1:
                mes = 2
            if fecha_tapa_issue.find("March")!=-1:
                mes = 3
            if fecha_tapa_issue.find("April")!=-1:
                mes = 4
            if fecha_tapa_issue.find("May")!=-1:
                mes = 5
            if fecha_tapa_issue.find("June")!=-1:
                mes = 6
            if fecha_tapa_issue.find("July")!=-1:
                mes = 7
            if fecha_tapa_issue.find("August")!=-1:
                mes = 8
            if fecha_tapa_issue.find("September")!=-1:
                mes = 9
            if fecha_tapa_issue.find("October")!=-1:
                mes = 10
            if fecha_tapa_issue.find("November")!=-1:
                mes = 11
            if fecha_tapa_issue.find("December")!=-1:
                mes = 12
            anio = int(fecha_tapa_issue[-4:])
            comicbook_info.fechaTapa = date(anio, mes,1)
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_story_arc, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.id_arco_argumental=match.group(1)
        matches = re.finditer(comic_vine_info_issue_searcher.regex_get_issue_url_cover, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.thumb_url=match.group(1)

        return comicbook_info

if __name__ == "__main__":
    comcis_org_searcher = comic_vine_info_issue_searcher()
    comcis_org_searcher.search_serie('https://comicvine.gamespot.com/green-lantern-39-agent-orange-part-1/4000-155207/')
    # cadena = 'June 2018'
    # print(cadena[:-4])
    # comcis_org_searcher.search_serie('https://comicvine.gamespot.com/batman-708-judgment-on-gotham-part-one-one-good-ma/4000-265991/')
    # comcis_org_searcher.search_serie('https://comicvine.gamespot.com/batman-713-in-storybook-endings/4000-286879/')