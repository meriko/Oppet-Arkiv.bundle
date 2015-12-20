TITLE = unicode('Öppet Arkiv')
PREFIX = '/video/oppetarkiv'

ICON  = 'icon-default.png'
ART = 'art-default.jpg'

BASE_URL = 'http://www.oppetarkiv.se'
ALL_PROGRAMS_URL = BASE_URL + '/program'

PROGRAMS_PER_PAGE = 12

####################################################################################################
def Start():

    ObjectContainer.title1 = TITLE
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'

####################################################################################################
@handler(PREFIX, TITLE)
def MainMenu():

    oc = ObjectContainer()
    element = HTML.ElementFromURL(BASE_URL + '/?embed=true')

    list_xpath = "//*[contains(@class, 'video-list')]"
    title_xpath = ".//h1/text()"
    
    for item in element.xpath(list_xpath):
        title = unicode(item.xpath(title_xpath)[0].strip())
        
        oc.add(
            DirectoryObject(
                key = Callback(
                    MainPrograms,
                    title_id = title,
                    url = BASE_URL,
                    list_xpath = list_xpath,
                    title_xpath = title_xpath
                ),
                title = title
            )
        )

    title = 'Kategorier'
    oc.add(
        DirectoryObject(
            key = Callback(Categories, title = title),
            title = title
        )
    )
    
    title = 'Nostalgitrippen'
    oc.add(
        DirectoryObject(
            key = Callback(NostalgiaChoice, title = title),
            title = title
        )
    )
        
    title = 'Alla Program'
    oc.add(
        DirectoryObject(
            key = Callback(Programs, title = title, url = ALL_PROGRAMS_URL),
            title = title
        )
    )

    title = unicode('Sök')
    oc.add(
        InputDirectoryObject(
            key = Callback(Search),
            title = title,
            prompt = title,
            thumb = R('search.png'),
            art = R(ART)
        )
    )
    
    return oc

####################################################################################################
# NOTE! Can't have a route on this one since Samsung can't handle it!
def Search(query):

    oc = ObjectContainer(title2='Resultat')
    element = HTML.ElementFromURL(BASE_URL + '/sok/?q=%s&embed=true' % unicode(String.Quote(query)))
    
    for program in element.xpath(".//*[contains(@href, '/video/')]"):
        link = BASE_URL + program.xpath("./@href")[0].strip()
        program_title = unicode(program.xpath("./@title")[0].strip())
        program_thumb_list = element.xpath('//img[@alt="' + program_title + '"]/@srcset')[0]
        program_thumb = program_thumb_list.split(",")[-1].strip().split(" ")[0]
        
        if program_thumb.startswith("//"):
            program_thumb = 'http:' + program_thumb
        
        slug, program_url = GetSlugAndURL(program_title, link)
        
        oc.add(
            DirectoryObject(
                key = Callback(ProgramVideos, url = program_url, title = program_title, slug = slug),
                title = program_title,
                thumb = program_thumb
            )
        )
    
    if len(oc) < 1:
        return ObjectContainer(header=unicode("Resultat"), message=unicode("Kunde inte hitta något för: ") + unicode(query))

    return oc

####################################################################################################
@route(PREFIX + '/nostalgiachoice')
def NostalgiaChoice(title):
    oc = ObjectContainer(title2=unicode(title))

    this_year = int(Datetime.Now().year)
    first_year = this_year - 100
    
    for year in reversed(range(first_year, this_year + 1 - 10)):
        title = unicode('Födelseår: ') + str(year)
        
        oc.add(
            DirectoryObject(
                key = Callback(Nostalgia, title = title, url = BASE_URL + '/nostalgi/%s' % year),
                title = title
            )
        )
        
    return oc

####################################################################################################
@route(PREFIX + '/nostalgia')
def Nostalgia(title, url):

    oc = ObjectContainer(title2=unicode(title))
    element = HTML.ElementFromURL(url)

    for video in element.xpath(".//*[contains(@href, '/video/')]"):
        url = BASE_URL + video.xpath("./@href")[0].strip()
        title = unicode(video.xpath("./@title")[0].strip())
        thumb_list = element.xpath("//img[@alt='" + title + "']/@srcset")[0]
        thumb = thumb_list.split(",")[-1].strip().split(" ")[0]
        
        if thumb.startswith("//"):
            thumb = 'http:' + thumb
        
        if '-avsnitt-' in url:
            slug, url = GetSlugAndURL(title, url)
            
            oc.add(
                DirectoryObject(
                    key = Callback(ProgramVideos, url = url, title = title, slug = slug),
                    title = title,
                    thumb = thumb
                )
            )
        else:
            oc.add(
                VideoClipObject(
                    url = url,
                    title = title,
                    thumb = thumb
                )
            )
        
    return oc

####################################################################################################
@route(PREFIX + '/mainprograms')
def MainPrograms(title_id, url, list_xpath, title_xpath):

    oc = ObjectContainer(title2=unicode(title_id))
    element = HTML.ElementFromURL(url)

    for item in element.xpath(list_xpath):
        try:
            if not (title_id == unicode(item.xpath(title_xpath)[0].strip())):
                continue
        except:
            continue
        
        for video in item.xpath(".//*[contains(@href, '/video/')]"):
            url = BASE_URL + video.xpath("./@href")[0].strip()
            title = unicode(video.xpath("./@title")[0].strip())
            thumb_list = item.xpath("//img[@alt='" + title + "']/@srcset")[0]
            thumb = thumb_list.split(",")[-1].strip().split(" ")[0]
            
            if thumb.startswith("//"):
                thumb = 'http:' + thumb
            
            if '-avsnitt-' in url:
                slug, url = GetSlugAndURL(title, url)
                
                oc.add(
                    DirectoryObject(
                        key = Callback(ProgramVideos, url = url, title = title, slug = slug),
                        title = title,
                        thumb = thumb
                    )
                )
            else:
                oc.add(
                    VideoClipObject(
                        url = url,
                        title = title,
                        thumb = thumb
                    )
                )
        
    return oc

####################################################################################################
@route(PREFIX + '/programs')
def Programs(title, url):

    oc = ObjectContainer(title2=unicode(title))
    element = HTML.ElementFromURL(ALL_PROGRAMS_URL)
    
    for item in element.xpath(".//*[contains(@href, '/etikett/titel/')]"):
        title = unicode(item.xpath(".//text()")[0]).strip()        
        url = GetProgramURL(title)
        
        oc.add(
            DirectoryObject(
                key = Callback(ProgramVideos, url = url, title = title),
                title = title
            )
        )
    return oc

####################################################################################################
@route(PREFIX + '/categories')
def Categories(title):

    oc = ObjectContainer(title2=unicode(title))
    element = HTML.ElementFromURL(BASE_URL + '/genrer')

    for item in element.xpath("//*[contains(@href, '/etikett/genre/')]"):
        title = unicode(''.join(item.xpath(".//text()")).strip())
        thumb = item.xpath(".//img/@src")[0].strip()
        url = BASE_URL + item.xpath("./@href")[0]
        
        if thumb.startswith("//"):
            thumb = 'http:' + thumb
        
        oc.add(
            DirectoryObject(
                key = Callback(CategoryPrograms, title = title, url = url),
                title = title,
                thumb = thumb
            )
        )
        
    return oc

####################################################################################################
@route(PREFIX + '/categoryprograms', page = int)
def CategoryPrograms(title, url, page = 1):

    oc = ObjectContainer(title2=unicode(title))
    
    for pages in range(5):
        try:
            element = HTML.ElementFromURL(url + '?titelsida=%s&sort=poang&embed=true' % page)
        except:
            break
        
        for program in element.xpath(".//*[contains(@href, '/video/')]"):
            link = BASE_URL + program.xpath("./@href")[0].strip()
            program_title = unicode(program.xpath("./@title")[0].strip())
            program_thumb_list = element.xpath('//img[@alt="' + program_title + '"]/@srcset')[0]
            program_thumb = program_thumb_list.split(",")[-1].strip().split(" ")[0]
            
            if program_thumb.startswith("//"):
                program_thumb = 'http:' + program_thumb
            
            slug, program_url = GetSlugAndURL(program_title, link)
            
            oc.add(
                DirectoryObject(
                    key = Callback(ProgramVideos, url = program_url, title = program_title, slug = slug),
                    title = program_title,
                    thumb = program_thumb
                )
            )
        
        page = page + 1
        
    return oc

####################################################################################################
@route(PREFIX + '/programvideos', page = int)
def ProgramVideos(title, url, slug = None, page = 1):

    oc = ObjectContainer(title2=unicode(title))
  
    for type in ['episodes', 'clips']:
        try:
            if slug:
                element = HTML.ElementFromURL(url + '%s/?titleTagName=%s&sida=%s&embed=true' % (type, slug, page))
            else:
                element = HTML.ElementFromURL(url + '/?sida=%s&sort=tid_stigande&embed=true' % page)
        except:
            break
    
        xpath = './/'
        if len(element.xpath("//aside")):
            xpath = './/aside//'
            
        for item in element.xpath("%s*[contains(@href, '/video/')]" % xpath):
            try:
                video_url = BASE_URL + item.xpath("./@href")[0].strip()
                video_title = unicode(item.xpath("./@title")[0].strip())
            except:
                continue
            
            try:
                video_thumb_list = element.xpath("//img[@alt='" + video_title + "']/@srcset")[0]
                video_thumb = video_thumb_list.split(",")[-1].strip().split(" ")[0]
            
                if video_thumb.startswith("//"):
                    video_thumb = 'http:' + video_thumb
            except:
                video_thumb = R(ICON)
            
            oc.add(
                VideoClipObject(
                    url = video_url,
                    title = video_title,
                    thumb = video_thumb,
                    source_title = 'SVT'
                )
            )
        
        if len(oc) > 0:
            
            element_string = HTML.StringFromElement(element)
            
            if 'Visa fler' in element_string or len(oc) >= PROGRAMS_PER_PAGE:
                oc.add(
                    NextPageObject(
                        key = Callback(
                            ProgramVideos,
                            title = title,
                            url = url,
                            slug = slug,
                            page = page + 1
                        ),
                        title = "Fler..."
                    )
                )
            break
    
    if len(oc) < 1:
        return ObjectContainer(header = "Inga program", message = unicode("Kunde inte hitta några program"))
     
    return oc

####################################################################################################
def GetProgramURL(title):
    slug = GetSlug(title)
    url = BASE_URL + '/etikett/titel/' + slug
    
    return url

####################################################################################################
def GetSlugAndURL(title, url):
    slug = GetSlug(title)
    url = url[:url.rfind("/") + 1]
    
    return slug, url

####################################################################################################
def GetSlug(title):
    slug = title
    
    if ':' in slug:
        slug = slug.split(":")[-1].strip()
        
    if '(' in slug:
        slug = slug.split("(")[0].strip()
        
    slug = slug.replace("å", "%c3%a5").replace("ä", "%c3%a4").replace("ö", "%c3%b6").replace("Å", "%c3%85").replace("Ä", "%c3%84").replace("Ö", "%c3%96").replace(" ", "_").replace(",", "")

    return slug