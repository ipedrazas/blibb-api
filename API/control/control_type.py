

class ControlType(object):

    TEXT = 1
    MULTITEXT = 2
    DATE = 3
    LIST = 4
    IMAGE = 21
    MP3 = 31
    DOC = 41
    URL = 51
    TWITTER = 61
    LIST = 69

    @classmethod
    def get_type(self, typex):
        res = "0x%0.2x" % typex
        return res[2:]

    @classmethod
    def is_multitext(self, typex):
        return typex == self.get_type(self.MULTITEXT)

    @classmethod
    def is_mp3(self, typex):
        return typex == self.get_type(self.MP3)

    @classmethod
    def is_image(self, typex):
        return typex == self.get_type(self.IMAGE)

    @classmethod
    def is_url(self, typex):
        return typex == self.get_type(self.URL)

    @classmethod
    def is_date(self, typex):
        return typex == self.get_type(self.DATE)

    @classmethod
    def is_twitter(self, typex):
        return typex == self.get_type(self.TWITTER)

    @classmethod
    def is_list(self, typex):
        return typex == self.get_type(self.LIST)
