from Extras import BabelComicBookManagerConfig
import os

class Publisher:
    def __init__(self,id,name):
        self.id = id
        self.name = name
        self.deck = ""
        self.description=""
        self.logoImagePath=""
    def hasLocalLogo(self):
        if self.logoImagePath:
            file_name = self.logoImagePath.split('/')[-1]
            file_name_no_ext = (file_name[:-4])
            if os.path.exists(BabelComicBookManagerConfig().getPublisherLogoPath() + file_name_no_ext + ".jpg"):
                return True
        return False
    def getLogoLocalPath(self):
        file_name = self.logoImagePath.split('/')[-1]
        file_name_no_ext = (file_name[:-4])
        if self.hasLocalLogo():
            return BabelComicBookManagerConfig().getPublisherLogoPath() + file_name_no_ext + ".jpg"