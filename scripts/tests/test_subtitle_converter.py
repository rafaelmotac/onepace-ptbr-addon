import os
import tempfile

import pytest

from subtitle_converter import ass_to_srt, convert_file_to_srt, convert_time

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestConvertTime:
    def test_standard_format(self):
        assert convert_time("0:01:15.00") == "00:01:15,000"

    def test_double_digit_hours(self):
        assert convert_time("1:30:45.50") == "01:30:45,500"

    def test_centiseconds(self):
        assert convert_time("0:00:00.99") == "00:00:00,990"

    def test_invalid_format_returns_unchanged(self):
        assert convert_time("invalid") == "invalid"

    def test_empty_string(self):
        assert convert_time("") == ""


class TestAssToSrt:
    @pytest.fixture()
    def sample_ass(self):
        with open(os.path.join(FIXTURES_DIR, "sample.ass"), encoding="utf-8") as f:
            return f.read()

    def test_converts_dialogue_lines(self, sample_ass):
        srt = ass_to_srt(sample_ass)
        assert "Eu sou Monkey D. Luffy!" in srt
        assert "Eu vou ser o Rei dos Piratas!" in srt

    def test_strips_ass_tags(self, sample_ass):
        srt = ass_to_srt(sample_ass)
        assert "{\\an8}" not in srt
        assert "{\\fad(500,500)}" not in srt

    def test_filters_sign_style(self, sample_ass):
        srt = ass_to_srt(sample_ass)
        assert "East Blue" not in srt

    def test_filters_song_style(self, sample_ass):
        srt = ass_to_srt(sample_ass)
        assert "We Are!" not in srt

    def test_filters_title_style(self, sample_ass):
        srt = ass_to_srt(sample_ass)
        assert "Romance Dawn" not in srt

    def test_converts_newline_markers(self, sample_ass):
        srt = ass_to_srt(sample_ass)
        assert "Vamos nessa!\nTodos juntos!" in srt

    def test_srt_numbering(self, sample_ass):
        srt = ass_to_srt(sample_ass)
        lines = srt.strip().split("\n")
        assert lines[0] == "1"

    def test_time_format_in_output(self, sample_ass):
        srt = ass_to_srt(sample_ass)
        assert "00:01:15,000 --> 00:01:18,500" in srt

    def test_empty_input(self):
        assert ass_to_srt("") == ""


class TestConvertFileToSrt:
    def test_converts_ass_file(self):
        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as tmp:
            output_path = tmp.name
        try:
            result = convert_file_to_srt(
                os.path.join(FIXTURES_DIR, "sample.ass"), output_path
            )
            assert result is True
            with open(output_path, encoding="utf-8") as f:
                content = f.read()
            assert "Luffy" in content
        finally:
            os.unlink(output_path)

    def test_copies_srt_directly(self):
        with tempfile.NamedTemporaryFile(
            suffix=".srt", mode="w", delete=False, encoding="utf-8"
        ) as src:
            src.write("1\n00:00:01,000 --> 00:00:02,000\nTest\n")
            src_path = src.name

        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as dst:
            dst_path = dst.name

        try:
            assert convert_file_to_srt(src_path, dst_path) is True
            with open(dst_path, encoding="utf-8") as f:
                assert "Test" in f.read()
        finally:
            os.unlink(src_path)
            os.unlink(dst_path)

    def test_unsupported_format(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"not a subtitle")
            tmp_path = tmp.name
        try:
            assert convert_file_to_srt(tmp_path, "/tmp/out.srt") is False
        finally:
            os.unlink(tmp_path)
