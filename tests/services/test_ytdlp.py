from app.services.ytdlp import parse_video_metadata


def test_parse_video_metadata_prefers_track_over_title():
    metadata = parse_video_metadata({"track": "Track Name", "title": "Video Title"})
    assert metadata["title"] == "Track Name"


def test_parse_video_metadata_falls_back_to_uploader_for_artist():
    metadata = parse_video_metadata({"title": "Video Title", "uploader": "Uploader Name"})
    assert metadata == {
        "title": "Video Title",
        "artist": "Uploader Name",
        "album": None,
    }
