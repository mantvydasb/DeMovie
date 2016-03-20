from html.parser import HTMLParser

MAX_LINKS = 5

class SearchResultsParser(HTMLParser):
    parsedTorrentsLinks = []
    linksCounter = 0

    def handle_starttag(self, tag, attrs):
        if (len(attrs) > 1):
            href = attrs[1][1]
            if tag == "a" and "download" in href and self.linksCounter < MAX_LINKS:
                href = href.replace(" ", ".").replace("%20", ".")
                self.parsedTorrentsLinks.append(href)
                self.linksCounter += 1
