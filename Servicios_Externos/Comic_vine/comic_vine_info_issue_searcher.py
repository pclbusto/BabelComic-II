import re
# esta clase ya hace referencia a esta clase
import Extras.ComicVineSearcher
import Extras.Config

from urllib.request import urlopen
from Entidades.Agrupado_Entidades import  Comicbook_Info,Comicbook_Info_Cover_Url, Arco_Argumental
from datetime import date
from Entidades import Init
import Entidades
import threading

class Comic_Vine_Info_Issue_Searcher():


    regex_search_serie = r"<td class=\"listing_publisher\"> <a href=\"/publisher/(\d*)/\">([^<]*)</a></td>[^<]*<td>" \
                         r" <a href=\"/series/(\d*)/\">([^<|]*)</a> (\[m\])*(\[b\])*</td>[^<]*<td> (\d*) </td>[^<]*<t" \
                         r"d style=\"text-align: right\"> (\d+) issues"
    regex_get_issue_number = r"Issue Number<\/th>[^<]*<td>[^<]*[^>]*[^<]*<span>(\d+)<\/span>"
    regex_get_issue_name = r"<th>Name<\/th>[^<]*<td>[^<][^>]*[^<]*<span>[^>]*>([^<]*)"
    regex_get_issue_description = r'<div class="wiki-item-display js-toc-content">[^<]*(.*)<\/div>[^<]*<div class="wiki-item-edit">[^<]*<div    id='
    regex_get_issue_cover_date= r'<th>Cover Date<\/th>[^<]*<td>[^<]*[^>]*[^<]*<span>([^<]*)'
    regex_get_issue_story_arc = r"4045-(\d*)"
    regex_get_issue_id_volume = r"4050-(\d*)"
    regex_get_issue_url_cover = r"img src=\"(https:\/\/static\.comicvine\.com\/uploads\/scale_large[^\"]*)"

    def __init__(self, session=None):
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

    def search_issue(self, url):
        html = urlopen(url).read().decode('utf-8')
        # print(html)
        comicbook_info = Comicbook_Info()
        matches = re.finditer(Comic_Vine_Info_Issue_Searcher.regex_get_issue_number, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.numero = match.group(1)
        matches = re.finditer(Comic_Vine_Info_Issue_Searcher.regex_get_issue_name, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.titulo = match.group(1)
        matches = re.finditer(Comic_Vine_Info_Issue_Searcher.regex_get_issue_description, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.resumen = match.group(1)
        matches = re.finditer(Comic_Vine_Info_Issue_Searcher.regex_get_issue_cover_date, html, re.DOTALL)
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
        matches = re.finditer(Comic_Vine_Info_Issue_Searcher.regex_get_issue_story_arc, html, re.DOTALL)
        # guardamos los arcos si es que tiene
        for matchNum, match in enumerate(matches):
            arco_argumental = Arco_Argumental()
            arco_argumental.id_arco_argumental = int(match.group(1))
            comicbook_info.ids_arco_argumental.append(arco_argumental)
        matches = re.finditer(Comic_Vine_Info_Issue_Searcher.regex_get_issue_url_cover, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comic_url =Comicbook_Info_Cover_Url(thumb_url=match.group(1))
            comicbook_info.thumbs_url.append(comic_url)
        comicbook_info.actualizado_externamente = True
        # retornamos un comic info con un id de arco. Que puede o no estar en la base eso lo resolvemos mas adelante
        return comicbook_info


if __name__ == "__main__":

    comcis_org_searcher = Comic_Vine_Info_Issue_Searcher()
    comicbook_info = comcis_org_searcher.search_issue('https://comicvine.gamespot.com/the-darkness-11-hearts-of-darkness-part-one/4000-118663/')
    print(comicbook_info)
