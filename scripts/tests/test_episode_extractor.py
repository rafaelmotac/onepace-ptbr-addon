import pytest

from subtitle_converter import extract_episode_number


class TestExtractEpisodeNumber:
    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("Romance Dawn 01.ass", 1),
            ("[One Pace] Alabasta 15 PTBR.ass", 15),
            ("Ep 03 - Something.srt", 3),
            ("wano_22_ptbr.ass", 22),
            ("01.ass", 1),
            ("episode_05.srt", 5),
            ("ep12.ass", 12),
            ("Dressrosa 100 ptbr.ass", 100),
        ],
    )
    def test_extracts_episode_number(self, filename, expected):
        assert extract_episode_number(filename) == expected

    def test_returns_none_for_no_number(self):
        assert extract_episode_number("readme.txt") is None

    def test_extracts_from_large_number(self):
        # "file_1000" matches "100" via the 3-digit generic pattern
        assert extract_episode_number("file_1000.ass") == 100

    def test_rejects_zero(self):
        assert extract_episode_number("ep_0.ass") is None
