import bruter
import xml.etree.ElementTree as xmlTree
import sys
import re
import conf
import results_parser


class Colours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Torrent:
    title           = ''
    description     = ''
    descriptionLink = ''
    uploadDate      = ''

    def __init__(self, title, description, link, uploadDate):
        self.title           = title
        self.description     = description
        self.descriptionLink = link
        self.downloadLink    = str(link).replace("details", "download").replace("&hit=1", "") + '&name=' + title.replace(" ", ".") + "_.torrent"
        self.uploadDate      = uploadDate

class Linkomanija():
    username   = conf.username
    password   = conf.password
    cookie     = conf.cookie
    bruter     = ''
    baseUrl    = "https://www.linkomanija.net/"
    loginUrl   = baseUrl + "takelogin.php"
    searchUrl  = baseUrl + "browse.php?incldead=0&search="
    moviesFeed = baseUrl + "rss.php?feed=link&cat[]=29&cat[]=52&cat[]=53&cat[]=61&passkey=14aba47f3165387ebaaf0aba38c140c2"
    toWatch    = \
        {
            'series': [
            "the big bang theory",
            "walking dead",
            "the 100",
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
            "narcos"
            ],
            'movies': [
                "spotlight",
                "criminals",
                "snowden",
		        "money monster",
                "mother's day",
                "a hologram for the king",
                "barbershop: the next cut",
                "neighbors 2: sorority rising",
                "the boss",
                "keanu",
                "miracles from heaven",
                "the meddler",
                "money monster",
                "secret in their eyes",
                "larry crown",
                "love, wedding, marriage",
                "hail, caesar",
            ]
        }
    searchResultsParser = results_parser.SearchResultsParser()
    parsedTorrentsCount = 0

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
                title = str(child.find("title").text)
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
                print(Colours.HEADER
                      + '[' + rating + Colours.ENDC + ' imdb] '
                      + Colours.WARNING + torrent.title + Colours.ENDC + Colours.HEADER + '  //  '
                      + Colours.ENDC + torrent.descriptionLink
                      + '\n' + torrent.downloadLink)

    def getLatestMoviesFeed(self):
        moviesFeed = self.sendRequest(self.moviesFeed)
        root = xmlTree.fromstring(moviesFeed)
        return root

    def getSearchResultsHTML(self, query):
        url = self.searchUrl + "'" + query + "'"
        url = url.replace(" ", "+")
        results = self.sendRequest(url)
        return results

    def getTorrentsToWatch(self):
        offset = 0
        printedTorrentsCount = 0
        foundTorrentsCount = 0

        for torrentType in self.toWatch:
            print("\n\n\n[*] Hunting torrents for your %s\n" % torrentType)

            for index, torrentTitle in enumerate(self.toWatch[torrentType]):
                foundTorrentsCount = self.searchRecentTorrentsByQuery(torrentTitle)
                print(Colours.OKGREEN + "[*] " + torrentTitle + Colours.ENDC)

                for torrentDownloadLink in self.searchResultsParser.parsedTorrentsLinks[printedTorrentsCount : (index + 1) * foundTorrentsCount + offset + 1]:
                    print(linkomanija.baseUrl + torrentDownloadLink)
                    printedTorrentsCount += 1
                print("\n")
            offset += printedTorrentsCount

    def searchRecentTorrentsByQuery(self, seriesTitle):
        searchResultsHtml = linkomanija.getSearchResultsHTML(seriesTitle)
        self.searchResultsParser = results_parser.SearchResultsParser()
        self.parsedTorrentsCount = self.searchResultsParser.parsedTorrentsLinks.__len__()
        self.searchResultsParser.feed(searchResultsHtml)
        torrentsFoundCount = self.searchResultsParser.parsedTorrentsLinks.__len__() - self.parsedTorrentsCount
        return torrentsFoundCount

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
        linkomanija.getTorrentsToWatch()

    input()
