import re

from urllib.request import urlopen
from Entidades.Agrupado_Entidades import  Comicbook_Info,Comicbook_Info_Cover_Url, Arco_Argumental
from datetime import date
from Entidades import Init
import Entidades

class Comic_Vine_Info_Searcher():


    regex_search_serie = r"<td class=\"listing_publisher\"> <a href=\"/publisher/(\d*)/\">([^<]*)</a></td>[^<]*<td>" \
                         r" <a href=\"/series/(\d*)/\">([^<|]*)</a> (\[m\])*(\[b\])*</td>[^<]*<td> (\d*) </td>[^<]*<t" \
                         r"d style=\"text-align: right\"> (\d+) issues"
    regex_get_issue_number = r"Issue Number<\/th>[^<]*<td>[^<]*[^>]*[^<]*<span>([^<]*)<\/span>"
    regex_get_issue_name = r"<th>Name<\/th>[^<]*<td>[^<][^>]*[^<]*<span>[^>]*>([^<]*)"
    regex_get_issue_description = r'<div class="wiki-item-display js-toc-content">[^<]*(.*)<\/div>[^<]*<div class="wiki-item-edit">[^<]*<div    id='
    regex_get_issue_cover_date= r'<th>Cover Date<\/th>[^<]*<td>[^<]*[^>]*[^<]*<span>([^<]*)'
    regex_get_issue_story_arc = r"4045-(\d*)/\">"
    regex_get_issue_id_volume = r"4050-(\d*)"
    #regex_get_issue_url_cover = r"img src=\"(https:\/\/static\.comicvine\.com\/uploads\/scale_large[^\"]*) "
    regex_get_issue_url_cover = r"img src=\"(http.*\/uploads\/scale_large[^\"]*)"

    regex_get_arcs_issues = r"/4000-(\d+)/\">[^\w|^\d^<]"
    regex_get_arcs_pages_count = r"\/issues\/\?page=\d+\">"

    def __init__(self, session=None):
        if session is None:
            self.session = Entidades.Init.Session()
        else:
            self.session = session

    def is_number(self, s):
        try:
            float(s)  # for int, long and float
        except ValueError:
            try:
                complex(s)  # for complex
            except ValueError:
                return False

        return True

    def search_issue(self, url):
        html = urlopen(url).read().decode('utf-8')
        #print(html)
        print(url)
        comicbook_info = Comicbook_Info()
        comicbook_info.url = url
        comicbook_info.api_detail_url = "https://comicvine.gamespot.com/api/issue/4000-"+url[url.rfind("-")+1:-1]
        matches = re.finditer(Comic_Vine_Info_Searcher.regex_get_issue_number, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.numero = match.group(1)
            if self.is_number(comicbook_info.numero):
                comicbook_info.orden = float(comicbook_info.numero)
            else:
                comicbook_info.orden = 0
        matches = re.finditer(Comic_Vine_Info_Searcher.regex_get_issue_name, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.titulo = match.group(1)
        matches = re.finditer(Comic_Vine_Info_Searcher.regex_get_issue_description, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comicbook_info.resumen = match.group(1)
        matches = re.finditer(Comic_Vine_Info_Searcher.regex_get_issue_cover_date, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            fecha_tapa_issue = match.group(1)
            # print(fecha_tapa_issue)
            mes=0
            if fecha_tapa_issue.find("January")!=-1:
                mes = 1
            elif fecha_tapa_issue.find("February")!=-1:
                mes = 2
            elif fecha_tapa_issue.find("March")!=-1:
                mes = 3
            elif fecha_tapa_issue.find("April")!=-1:
                mes = 4
            elif fecha_tapa_issue.find("May")!=-1:
                mes = 5
            elif fecha_tapa_issue.find("June")!=-1:
                mes = 6
            elif fecha_tapa_issue.find("July")!=-1:
                mes = 7
            elif fecha_tapa_issue.find("August")!=-1:
                mes = 8
            elif fecha_tapa_issue.find("September")!=-1:
                mes = 9
            elif fecha_tapa_issue.find("October")!=-1:
                mes = 10
            elif fecha_tapa_issue.find("November")!=-1:
                mes = 11
            elif fecha_tapa_issue.find("December")!=-1:
                mes = 12
            else:
                mes = 12
            anio_str = fecha_tapa_issue[-4:]
            anio = 1900
            if anio_str.isdigit():
                anio = int(fecha_tapa_issue[-4:])
            print("Datos para la fecha del comicbookinfo: {}".format(date(anio, mes, 1)))
            comicbook_info.fecha_tapa = date(anio, mes, 1).toordinal()
            print("Datos COMIC SCRAPER \n{}".format(comicbook_info))
            print("HASTA ACA")
        matches = re.finditer(Comic_Vine_Info_Searcher.regex_get_issue_story_arc, html, re.DOTALL)
        # guardamos los arcos si es que tiene
        for matchNum, match in enumerate(matches):
            arco_argumental = Arco_Argumental()
            arco_argumental.id_arco_argumental = int(match.group(1))
            comicbook_info.lista_ids_arcos_para_procesar.append(arco_argumental)
        matches = re.finditer(Comic_Vine_Info_Searcher.regex_get_issue_url_cover, html)
        print("URL Imagenes covers")
        counter = 0
        for matchNum, match in enumerate(matches):
            comic_url =Comicbook_Info_Cover_Url(thumb_url=match.group(1))
            print("URL:{}".format(comic_url.thumb_url))
            comicbook_info.thumbs_url.append(comic_url)
            counter +=1
        print("URL Imagenes covers {}".format(counter))

        comicbook_info.actualizado_externamente = True
        # retornamos un comic info con un id de arco. Que puede o no estar en la base eso lo resolvemos mas adelante
        return comicbook_info

    def search_issues_in_arc(self, url):
        html = urlopen(url).read().decode('utf-8')
        # print(url)
        lista_ids_issues_para_procesar = []
        cantidad_paginas = 0

        matches = re.finditer(Comic_Vine_Info_Searcher.regex_get_arcs_pages_count, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            cantidad_paginas+=1
        if cantidad_paginas>1:
            for i in range(1, cantidad_paginas+1):
                # print(url+"?page={}".format(i))
                html = urlopen(url+"?page={}".format(i)).read().decode('utf-8')
                matches = re.finditer(Comic_Vine_Info_Searcher.regex_get_arcs_issues, html, re.DOTALL)
                for matchNum, match in enumerate(matches):
                    lista_ids_issues_para_procesar.append(int(match.group(1)))
        else:
            matches = re.finditer(Comic_Vine_Info_Searcher.regex_get_arcs_issues, html, re.DOTALL)
            for matchNum, match in enumerate(matches):
                lista_ids_issues_para_procesar.append(int(match.group(1)))

        return  lista_ids_issues_para_procesar
if __name__ == "__main__":

    comcis_org_searcher = Comic_Vine_Info_Searcher()
    comcis_org_searcher.search_issue("https://comicvine.gamespot.com/witchblade-9-good-intentions-part-three/4000-691312/")
    # lista = comcis_org_searcher.search_issues_in_arc('https://comicvine.gamespot.com/faces-of-evil/4045-55781/issues/')
    # print(lista)
