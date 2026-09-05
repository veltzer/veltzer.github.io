"""Tests for import_books.py, which flattens books_read.yaml from ../data.

The source nests names, authors, ownings and readings per language; the media
page wants one flat item per book. These pin the rules that are easy to get
subtly wrong: which name and which id win, which reading supplies the rating,
and that ids survive a YAML round trip as strings.
"""

import import_books
import yaml


def book(**overrides):
    base = {
        "names": [
            {"language": "english", "name": "Black Box", "goodreads_id": "158856"},
            {"language": "hebrew", "name": "קופסה שחורה"},
        ],
        "authors": [[{"language": "english", "name": "Amos Oz"}, {"language": "hebrew", "name": "עמוס עוז"}]],
        "language": "hebrew",
        "ownings": [{"language": "hebrew"}],
        "readings": [
            {"language": "hebrew", "date": "2005-03-04T13:41:08Z", "timezone": "Asia/Jerusalem", "rating": 6, "review": "not bad"},
            {"language": "english", "date": "2021-04-23T12:21:58Z", "timezone": "Asia/Jerusalem", "rating": 8, "review": "better"},
        ],
    }
    base.update(overrides)
    return base


class TestNames:
    def test_english_name_is_the_card_name_and_hebrew_kept_aside(self):
        out = import_books.convert_item(book())
        assert out["name"] == "Black Box"
        assert out["name_he"] == "קופסה שחורה"

    def test_hebrew_only_book_uses_the_hebrew_name(self):
        out = import_books.convert_item(book(names=[{"language": "hebrew", "name": "שחמט", "simania_id": "11971"}]))
        assert out["name"] == "שחמט"
        assert "name_he" not in out

    def test_authors_join_english_names(self):
        out = import_books.convert_item(book(authors=[
            [{"language": "english", "name": "Margaret Weis"}],
            [{"language": "english", "name": "Tracy Hickman"}],
        ]))
        assert out["authors"] == "Margaret Weis, Tracy Hickman"
        assert out["author_list"] == ["Margaret Weis", "Tracy Hickman"]

    def test_no_authors(self):
        out = import_books.convert_item(book(authors=[]))
        assert out["authors"] == ""
        assert out["author_list"] == []


class TestIdsAndCover:
    def test_goodreads_id_gives_cover_and_url(self):
        out = import_books.convert_item(book())
        assert out["goodreads_id"] == "158856"
        assert out["cover"] == "goodreads-158856"
        assert out["url"] == "https://www.goodreads.com/book/show/158856"

    def test_simania_wins_over_goodreads(self):
        names = [
            {"language": "english", "name": "Chess", "goodreads_id": "1"},
            {"language": "hebrew", "name": "שחמט", "simania_id": "11971"},
        ]
        out = import_books.convert_item(book(names=names))
        assert out["cover"] == "simania-11971"
        assert out["url"] == "https://simania.co.il/bookdetails.php?item_id=11971"
        assert out["goodreads_id"] == "1"

    def test_known_no_cover_key_keeps_id_and_url_but_no_cover(self):
        key = sorted(import_books.NO_COVER)[0]
        book_id = key.split("-", 1)[1]
        out = import_books.convert_item(book(names=[{"language": "hebrew", "name": "X", "simania_id": book_id}]))
        assert out["simania_id"] == book_id
        assert out["url"].endswith(book_id)
        assert "cover" not in out

    def test_no_id_means_no_cover(self):
        out = import_books.convert_item(book(names=[{"language": "english", "name": "X"}]))
        assert "cover" not in out
        assert "url" not in out

    def test_ids_are_quoted_strings_after_a_yaml_round_trip(self):
        out = import_books.convert_item(book(names=[{"language": "english", "name": "X", "goodreads_id": "0123"}]))
        dumped = yaml.dump({"items": [out]}, default_flow_style=False, sort_keys=False, allow_unicode=True)
        assert '"0123"' in dumped
        assert yaml.safe_load(dumped)["items"][0]["goodreads_id"] == "0123"


class TestReadings:
    def test_latest_dated_reading_supplies_rating_and_review(self):
        out = import_books.convert_item(book())
        assert out["rating"] == 8
        assert out["review"] == "better"
        assert out["last_read"] == "2021-04-23T12:21:58Z"
        assert out["read_count"] == 2
        assert out["languages_read"] == ["english", "hebrew"]
        assert [r["date"] for r in out["readings"]] == ["2021-04-23T12:21:58Z", "2005-03-04T13:41:08Z"]
        assert "subtitle" not in out

    def test_undated_readings_have_no_rating_and_get_a_subtitle(self):
        out = import_books.convert_item(book(readings=[{"language": "hebrew", "undated": True}] * 2, ownings=[]))
        assert "rating" not in out
        assert "last_read" not in out
        assert "review" not in out
        assert out["read_count"] == 2
        assert out["readings"][0]["undated"] is True
        assert out["subtitle"] == "Read 2 times in hebrew; date unknown"

    def test_owned_unread_book(self):
        out = import_books.convert_item(book(readings=[], ownings=[{"language": "english"}]))
        assert out["read_count"] == 0
        assert out["owned_languages"] == ["english"]
        assert out["subtitle"] == "Not read yet; owned in english"

    def test_undated_after_dated(self):
        out = import_books.convert_item(book(readings=[
            {"language": "hebrew", "undated": True},
            {"language": "english", "date": "2021-04-23T12:21:58Z", "timezone": "UTC", "rating": 7, "review": "ok"},
        ]))
        assert out["readings"][0]["date"] == "2021-04-23T12:21:58Z"
        assert out["readings"][1]["undated"] is True
        assert out["rating"] == 7


class TestOptionalFields:
    def test_publisher_isbn_remark_pass_through(self):
        out = import_books.convert_item(book(publisher="Keter", isbn="1-2-3", remark="was named: Kufsa Shora"))
        assert out["publisher"] == "Keter"
        assert out["isbn"] == "1-2-3"
        assert out["remark"] == "was named: Kufsa Shora"

    def test_absent_optional_fields_are_not_emitted(self):
        out = import_books.convert_item(book())
        for field in ("publisher", "isbn", "remark"):
            assert field not in out


class TestConvert:
    def test_convert_wraps_items(self):
        out = import_books.convert({"items": [book(), book()]})
        assert len(out["items"]) == 2

    def test_convert_handles_missing_items(self):
        assert import_books.convert({}) == {"items": []}
