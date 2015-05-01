__author__ = 'cahitonur'


class Torrent:
    def __init__(self, title=None, url=None, seeders=None, leechers=None, size=None, source=None):
        self.title = title
        self.url = url
        self.seeders = seeders
        self.leechers = leechers
        self.size = size
        self.source = source

    def __unicode__(self):
        return self.title