from mediaarchiver import CONFIG, Directory
from mediaarchiver.media_archiving_step import MediaArchivingStep
from mediaarchiver.sites import Site
from mediaarchiver.sites.twitter import Twitter


class MediaArchiver:
    @classmethod
    def execute(cls) -> None:
        CONFIG.load()
        MediaArchivingStep(Twitter(Site.TWITTER.value)).execute(Directory.DOWNLOAD.value)
