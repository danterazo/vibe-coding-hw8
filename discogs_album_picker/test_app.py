import random
import unittest

from app import PickerError, media_labels, random_physical_release


def release(release_id, formats, title="Test album"):
    return {
        "basic_information": {
            "id": release_id,
            "title": title,
            "artists": [{"name": "Test artist"}],
            "formats": formats,
            "year": 2001,
            "thumb": "https://example.test/cover.jpg",
        }
    }


def page(releases, items=1, pages=1):
    return {"pagination": {"items": items, "pages": pages}, "releases": releases}


class MediaLabelTests(unittest.TestCase):
    def test_discards_digital_and_names_lp(self):
        formats = [
            {"name": "File", "qty": "1", "descriptions": ["MP3"]},
            {"name": "Vinyl", "qty": "1", "descriptions": ["LP", "Album"]},
            {"name": "CD", "qty": "2", "descriptions": ["Album"]},
        ]

        self.assertEqual(media_labels(formats), ["LP", "2 × CD"])

    def test_rejects_releases_without_physical_formats(self):
        self.assertEqual(media_labels([{"name": "Digital Media", "qty": "1"}]), [])
        self.assertEqual(media_labels([]), [])


class CollectionSelectionTests(unittest.TestCase):
    def test_finds_physical_release_on_another_page(self):
        digital = release(1, [{"name": "File", "qty": "1"}])
        vinyl = release(2, [{"name": "Vinyl", "qty": "1", "descriptions": ["LP"]}])
        responses = {1: page([digital], items=101, pages=2), 2: page([vinyl], items=101, pages=2)}
        requested = []

        def reader(username, token, page_number):
            requested.append(page_number)
            return responses[page_number]

        album = random_physical_release("listener-pages", "token", reader, random.Random(4))

        self.assertEqual(requested, [1, 2])
        self.assertEqual(album["artist"], "Test artist")
        self.assertEqual(album["media"], ["LP"])
        self.assertEqual(album["title"], "Test album")

    def test_reports_digital_only_collection(self):
        data = page([release(1, [{"name": "File", "qty": "1"}])])

        with self.assertRaisesRegex(PickerError, "No non-digital releases"):
            random_physical_release("listener-digital", "token", lambda *_: data)

    def test_rejects_invalid_username_before_api_call(self):
        def fail_if_called(*_args):
            self.fail("API reader should not be called for invalid input.")

        with self.assertRaisesRegex(PickerError, "valid Discogs username"):
            random_physical_release("bad username", "token", fail_if_called)

    def test_scans_every_page_for_a_uniform_pick(self):
        requested = []

        def reader(_username, _token, page_number):
            requested.append(page_number)
            data = page([release(page_number, [{"name": "CD", "qty": "1"}])], items=5000, pages=50)
            return data

        album = random_physical_release("listener-large", "token", reader, random.Random(2))

        self.assertEqual(requested, list(range(1, 51)))
        self.assertIn(int(album["url"].rsplit("/", 1)[-1]), range(1, 51))

    def test_revalidates_page_one_before_reusing_cache(self):
        requested = []
        data = page([release(1, [{"name": "CD", "qty": "1"}])])

        def reader(_username, _token, page_number):
            requested.append(page_number)
            return data

        random_physical_release("listener-cache", "first-token", reader)
        random_physical_release("listener-cache", "second-token", reader)

        self.assertEqual(requested, [1, 1])


if __name__ == "__main__":
    unittest.main()
