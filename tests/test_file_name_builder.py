from datetime import datetime

import pytest

from mediaarchiver.file_name_builder import DefaultFileNameBuilder


class TestDefaultFileNameBuilder:
    @staticmethod
    @pytest.mark.parametrize(
        "created_date_time, url, expected",
        [
            (
                datetime(2019, 8, 7, 21, 34, 45),
                "https://pbs.twimg.com/media/CeBmNUIUUAAZoQ3?format=jpg&name=medium",
                "20190807213445pbs.twimg.com_media_CeBmNUIUUAAZoQ3",
            ),
            (
                datetime(2019, 8, 7, 21, 50, 15),
                "https://stat.ameba.jp/user_images/20190101/21/shingokatori-official/27/45/j/o1080108014331554765.jpg",
                "20190807215015stat.ameba.jp_user_images_20190101_21_"
                "shingokatori-official_27_45_j_o1080108014331554765.jpg",
            ),
            (
                datetime(2019, 8, 8, 1, 48, 10),
                (
                    "https://instagram.fkix2-2.fna.fbcdn.net/vp/"
                    "b834511adcf6dcfd723df656e4d0286f/5DE02728/t51.2885-15/e35/"
                    "s1080x1080/64990884_2335764689840354_8806997272955239313_n.jpg?"
                    "_nc_ht=instagram.fkix2-2.fna.fbcdn.net"
                ),
                (
                    "20190808014810instagram.fkix2-2.fna.fbcdn.net_vp_"
                    "b834511adcf6dcfd723df656e4d0286f_5DE02728_t51.2885-15_e35_"
                    "s1080x1080_64990884_2335764689840354_8806997272955239313_n.jpg"
                ),
            ),
        ],
    )
    def test(created_date_time, url, expected):
        assert DefaultFileNameBuilder.build(created_date_time, url) == expected
