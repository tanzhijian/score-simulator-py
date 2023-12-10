from score_simulator_py.models import Match

matches_data: dict[str, list[Match]] = {
    "2023-12-08": [
        {
            "name": "Juventus vs Napoli",
            "utc_time": "2023-12-08T19:45:00.000Z",
            "finished": True,
            "competition": {
                "name": "Serie A",
                "logo": "https://img.legaseriea.it/vimages/62cef685/SerieA_RGB.jpg?webp&q=70&size=-x0",
            },
            "home": {
                "name": "Juventus",
                "logo": "https://img.legaseriea.it/vimages/62cfda28/colore=BLACK.png",
                "shots": 195,
                "xg": 22.7,
                "score": 1,
                "played": 15,
            },
            "away": {
                "name": "Napoli",
                "logo": "https://img.legaseriea.it/vimages/62cef532/napoli.png",
                "shots": 242,
                "xg": 25.6,
                "score": 0,
                "played": 15,
            },
        },
    ]
}


def test_match_model() -> None:
    match = matches_data["2023-12-08"][0]
    assert match["home"]["name"] == "Juventus"
