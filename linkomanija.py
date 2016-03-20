import bruter
import xml.etree.ElementTree as xmlTree
import sys
import re
import conf
import results_parser


class Torrent:
    title       = ''
    description = ''
    link        = ''
    uploadDate  = ''

    def __init__(self, title, description, link, uploadDate):
        self.title = title
        self.description = description
        self.link = link
        self.torrentLink = str(link).replace("details", "download").replace("&hit=1","") + '&name=' + title + "_.torrent"
        self.uploadDate = uploadDate


class Linkomanija():
    username    = conf.username
    password    = conf.password
    cookie      = conf.cookie
    bruter      = ''
    baseUrl     = "https://www.linkomanija.net/"
    loginUrl    = baseUrl + "takelogin.php"
    searchUrl   = baseUrl + "browse.php?incldead=0&search="
    moviesFeed  = baseUrl + "rss.php?feed=link&cat[]=29&cat[]=52&cat[]=53&cat[]=61&passkey=14aba47f3165387ebaaf0aba38c140c2"
    mySeries    = [
        "the big bang theory",
        "the 100",
        "walking dead",
        "master of none",
        "ballers",
        "the suits",
        "louie ck",
        "last ship",
        "odd couple",
        "fear the walking dead",
        "inside amy schumer",
        "episodes",
        "fargo",
        "homeland",
        "modern family",
        "mr robot",
        "silicon valley",
        "halt and catch fire",
        "the x-files",
    ]
    searchResultsParser = {}
    searchResultsHTML = {}

    def __init__(self):
        self.bruter = bruter.Bruter(
            loginUrl=self.loginUrl,
            usernameField="username",
            passwordField="password",
            headers={"Cookie": self.cookie}
        )
        self.login()

    def login(self):
        response = self.bruter.attemptLogin(username=self.username, password=self.password)
        return response

    def parseMoviesFeed(self, feed):
        torrents = []

        for child in feed[0]:
            if child.tag == "item":
                title = str(child.find("title").text).replace(" ", ".")
                description = child.find("description").text
                link = child.find("link").text
                uploadDate = child.find("pubDate").text
                torrent = Torrent(title, description, link, uploadDate)
                torrents.append(torrent)
        return torrents

    def sendRequest(self, url):
        response = self.bruter.getUrlContent(url, self.bruter.headers)
        return response

    def extractDecentlyRatedMovies(self, torrents):
      for torrent in torrents:
            isDecentlyRated = re.search('(<b>Rating:<\/b> [6-9.]+\w)', torrent.description)
            if isDecentlyRated:
                rating = isDecentlyRated.group(0).strip("<b>Rating:</b> ")
                print("[%s imdb] %s  [>]  %s \n%s \n" %(rating, torrent.title, torrent.link, torrent.torrentLink))

    def getLatestMoviesFeed(self):
        moviesFeed = self.sendRequest(self.moviesFeed)
        root = xmlTree.fromstring(moviesFeed)
        return root

    def getSearchResultsHTML(self, query):
        url = self.searchUrl + "'" + query + "'"
        url = url.replace(" ", "+")
        results = self.sendRequest(url)
        return results

    def getRecentTorrentsForMySeries(self):
        print("\n\n\n[*] Please wait, hunting torrents for your series...\n")

        for index, seriesTitle in enumerate(self.mySeries):
            maxLinks = results_parser.MAX_LINKS
            self.searchRecentTorrentsByQuery(seriesTitle)

            print("[*] " + seriesTitle)
            for torrentLink in self.searchResultsParser.parsedTorrentsLinks[index * maxLinks : (index + 1) * maxLinks]:
                print(linkomanija.baseUrl + torrentLink)
            print("\n")

    def searchRecentTorrentsByQuery(self, seriesTitle):
        searchResultsHtml = linkomanija.getSearchResultsHTML(seriesTitle)
        self.searchResultsParser = results_parser.SearchResultsParser()
        self.searchResultsParser.feed(searchResultsHtml)

    def getTorrentsByQuery(self, query):
        self.searchRecentTorrentsByQuery(query)
        print("[*] Torrents for %s" % query)
        [print(self.baseUrl + link) for link in self.searchResultsParser.parsedTorrentsLinks]

    def getRecentDecentMovies(self):
        latestMoviesFeed = linkomanija.getLatestMoviesFeed()
        torrents = linkomanija.parseMoviesFeed(latestMoviesFeed)
        linkomanija.extractDecentlyRatedMovies(torrents)

if __name__ == '__main__':
    linkomanija = Linkomanija()

    if sys.argv.__len__() > 1:
        query = sys.argv[1].replace(" ", "+")
        linkomanija.getTorrentsByQuery(query)
    else:
        linkomanija.getRecentDecentMovies()
        linkomanija.getRecentTorrentsForMySeries()