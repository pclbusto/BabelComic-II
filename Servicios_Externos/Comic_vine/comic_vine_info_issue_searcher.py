import re
# esta clase ya hace referencia a esta clase
import Extras.ComicVineSearcher
import Extras.Config

from urllib.request import urlopen
from Entidades.Agrupado_Entidades import  Comicbooks_Info,Comicbook_Info_cover_url, ArcoArgumental
from datetime import date
from Entidades import Init


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
    regex_get_issue_url_cover = r"(https://static.comicvine.com/uploads/scale_large[^\"]*)"

    def __init__(self):
        pass

    def search_serie(self, url):
        html = urlopen(url).read().decode('utf-8')
        # print(html)
        comicbook_info = Comicbooks_Info()
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
        for matchNum, match in enumerate(matches):
            arco_argumental = ArcoArgumental()
            arco_argumental.id_arco_argumental_externo = match.group(1)
            session = Init.Session()
            existe = session.query(ArcoArgumental).filter(
                ArcoArgumental.id_arco_argumental_externo == arco_argumental.id_arco_argumental_externo).first()
            if existe is None:
                #buscamos los datos del arco
                config = Extras.Config.Config()
                comicVineSearcher = Extras.ComicVineSearcher.ComicVineSearcher(config.getClave('story_arc_credits'), session=session)
                comicVineSearcher.setEntidad('story_arc_credits')
                arco_argumental = comicVineSearcher.getVineEntity(arco_argumental.id_arco_argumental_externo)
                session.add(arco_argumental)
                session.commit()
            comicbook_info.ids_arco_argumental.append(arco_argumental)

        matches = re.finditer(Comic_Vine_Info_Issue_Searcher.regex_get_issue_url_cover, html, re.DOTALL)
        for matchNum, match in enumerate(matches):
            comic_url =Comicbook_Info_cover_url(thumb_url=match.group(1))
            print(comic_url)
            comicbook_info.thumbs_url.append(comic_url)

        return comicbook_info


if __name__ == "__main__":

    comcis_org_searcher = Comic_Vine_Info_Issue_Searcher()
    comcis_org_searcher.search_stotyarc('https://comicvine.gamespot.com/blackest-night/4045-55766/issues/')

    # comcis_org_searcher.search_serie('https://comicvine.gamespot.com/green-lantern-39-agent-orange-part-1/4000-155207/')
    # cadena = 'June 2018'
    # print(cadena[:-4])
    # comcis_org_searcher.search_serie('https://comicvine.gamespot.com/batman-708-judgment-on-gotham-part-one-one-good-ma/4000-265991/')
    # comcis_org_searcher.search_serie('https://comicvine.gamespot.com/batman-713-in-storybook-endings/4000-286879/')