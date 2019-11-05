from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from parallelmediadownloader.parallel_media_downloader import ParallelMediaDownloader

from mediaarchiver.article import Article
from mediaarchiver.download_order_generator import DownloadOrderGenerator
from mediaarchiver.micro_image_filter import MicroImageFilter
from tests.testlibraries.instance_resource import InstanceResource


class TestDownloadOrderGenerator:
    @staticmethod
    def test_integration(tmp_path, mock_aioresponse):
        base_url = 'https://stat.ameba.jp'
        url1 = '/user_images/20181027/14/da-pump-blog/70/01/j/o1080097814291864857.jpg'
        url2 = '//stat.ameba.jp/user_images/20181027/14/da-pump-blog/6f/ca/j/o1080081014291864864.jpg'
        url3 = '/user_images/20181107/10/da-pump-blog/fe/e6/j/o1080080814298686921.jpg'
        url4 = 'https://stat.ameba.jp/user_images/20181107/10/da-pump-blog/1d/92/j/o1080080914298686924.jpg'
        download_order_generator = DownloadOrderGenerator(base_url, tmp_path, [
            Article(datetime(2018, 10, 27, 14, 20, 44), [url1, url2]),
            Article(datetime(2018, 11, 7, 10, 16, 24), [url3, url4]),
        ])
        @dataclass
        class Expected:
            url: str
            status: int
            file_path: Path
            content: bytes

        list_expected = [
            Expected(f'{base_url}{url1}', 200, tmp_path / (
                '20181027142044stat.ameba.jp_user_images_20181027_14_'
                'da-pump-blog_70_01_j_o1080097814291864857.jpg'
            ), InstanceResource.PATH_FILE_IMAGE_97_97_BLUE.read_bytes()),
            Expected(f'https:{url2}', 200, tmp_path / (
                '20181027142044stat.ameba.jp_user_images_20181027_14_'
                'da-pump-blog_6f_ca_j_o1080081014291864864.jpg'
            ), InstanceResource.PATH_FILE_IMAGE_97_97_GREEN.read_bytes()),
            Expected(f'{base_url}{url3}', 200, tmp_path / (
                '20181107101624stat.ameba.jp_user_images_20181107_10_'
                'da-pump-blog_fe_e6_j_o1080080814298686921.jpg'
            ), InstanceResource.PATH_FILE_IMAGE_97_97_RED.read_bytes()),
            Expected(f'{url4}', 200, tmp_path / (
                '20181107101624stat.ameba.jp_user_images_20181107_10_'
                'da-pump-blog_1d_92_j_o1080080914298686924.jpg'
            ), InstanceResource.PATH_FILE_IMAGE_97_97_YELLOW.read_bytes()),
        ]
        for expected in list_expected:
            mock_aioresponse.get(expected.url, status=200, body=expected.content)
        list_media_download_result = ParallelMediaDownloader.execute(
            download_order_generator, media_filter=MicroImageFilter()
        )

        assert len(list_media_download_result) == len(list_expected)
        for media_download_result, expected in zip(list_media_download_result, list_expected):
            assert media_download_result.url == expected.url
            assert media_download_result.status == expected.status
            assert media_download_result.media_file.path_file == expected.file_path
            assert media_download_result.media_file.path_file.read_bytes() == expected.content
