from parallelmediadownloader.media_file import MediaFile
from parallelmediadownloader.media_filter import NotImageFilter
from PIL import Image


class MicroImageFilter(NotImageFilter):
    PIXEL_EMOJI_AMEBA_BLOG: int = 96
    """Referenced Emoji on Ameba blog as Default threshold."""

    def __init__(
        self, *, threshold_width: int = PIXEL_EMOJI_AMEBA_BLOG, threshold_height: int = PIXEL_EMOJI_AMEBA_BLOG
    ):
        self.threshold_width = threshold_width
        self.threshold_height = threshold_height

    def _filter(self, media_file: MediaFile) -> bool:
        if super()._filter(media_file):
            return True
        with Image.open(media_file.path_file) as image:
            width, height = image.size
        return width <= self.threshold_width or height <= self.threshold_height
