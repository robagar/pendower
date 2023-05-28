from dataclasses import dataclass
import arrow
import requests
import json


@dataclass
class Spot:
    name: str
    latitude: float
    longitude: float

@dataclass
class Weather:
    time: arrow.Arrow
    wave_height: float

class Stormglass:
    def __init__(self, config, data_dir):
        self._api_key = config["api_key"]
        self._data_dir = data_dir

        self._weather_data_file = data_dir / 'weather.json'

    def get_weather(self, spot, time_span, *params):
        '''
        'waveHeight,wavePeriod,swellHeight,swellDirection,waterTemperature,airTemperature,windSpeed,windDirection'
        '''
        f = self._weather_data_file
        if not f.exists() or self._is_stale(f):
            print("[Stormglass] fetching weather data...")
            raw_data = self._fetch_weather(spot, time_span, *params)
            # cache for reuse
            self._save_data(raw_data, f)
        else:
            print("[Stormglass] using cached weather data")
            raw_data = self._load_data(f)

        return self._prepare_weather_data(raw_data)

    def _fetch_weather(self, spot, time_span, *params):
        (time_from, time_to) = time_span
        response = requests.get(
          'https://api.stormglass.io/v2/weather/point',
          params={
            'lat': spot.latitude,
            'lng': spot.longitude,
            'params': ",".join(params),
            'source': 'sg', # automatically choose best source
            'start': time_from.timestamp(),
            'end': time_to.timestamp()
          },
          headers={
            'Authorization': self._api_key
          }
        )

        # raise an exception if anything was wrong
        response.raise_for_status()

        # ...all good
        return response.json()

    def _save_data(self, data, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _load_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _is_stale(self, file_path):
        # TODO
        return False

    def _prepare_weather_data(self, raw_data):
        def value(d, name):
            v = d.get(name)
            return v["sg"] if v else None

        return list(map(lambda d: Weather(
            time=arrow.get(d["time"]), 
            wave_height=value(d, "waveHeight")
        ), raw_data["hours"]))


