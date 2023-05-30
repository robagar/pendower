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


@dataclass
class Tide:
    time: arrow.Arrow
    description: str
    height: float


@dataclass
class Astronomy:
    time: arrow.Arrow
    sunrise: arrow.Arrow
    sunset: arrow.Arrow
    moonrise: arrow.Arrow
    moonset: arrow.Arrow
    astronomical_dawn: arrow.Arrow
    astronomical_dusk: arrow.Arrow
    nautical_dawn: arrow.Arrow
    nautical_dusk: arrow.Arrow
    civil_dawn: arrow.Arrow
    civil_dusk: arrow.Arrow


class Stormglass:
    def __init__(self, config, data_dir):
        self._api_key = config["api_key"]
        self._data_dir = data_dir

        self._weather_data_file = data_dir / 'weather.json'
        self._tide_data_file = data_dir / 'tides.json'
        self._astonomy_data_file = data_dir / 'astronomy.json'

    def get_weather(self, spot, time_span, *weather_params):
        '''
        'waveHeight,wavePeriod,swellHeight,swellDirection,waterTemperature,airTemperature,windSpeed,windDirection'
        '''
        raw_data = self._load_or_fetch_data(
            self._weather_data_file, 
            "weather/point", 
            spot, 
            time_span, 
            params=",".join(weather_params))

        return self._prepare_weather_data(raw_data)

    def _prepare_weather_data(self, raw_data):
        def value(d, name):
            v = d.get(name)
            return v["sg"] if v else None

        return list(map(lambda d: Weather(
            time=arrow.get(d["time"]), 
            wave_height=value(d, "waveHeight")
        ), raw_data["hours"]))

    def get_tides(self, spot, time_span):
        (f,t) = time_span
        time_span = (f.shift(hours=-12), t.shift(hours=+12))

        raw_data = self._load_or_fetch_data(
            self._tide_data_file, 
            "tide/extremes/point", 
            spot, 
            time_span)

        return self._prepare_tide_data(raw_data)

    def _prepare_tide_data(self, raw_data):
        return list(map(lambda d: Tide(
            time=arrow.get(d["time"]),
            description=d["type"], 
            height=d["height"]
        ), raw_data["data"]))

    def get_astronomy(self, spot, time_span):
        raw_data = self._load_or_fetch_data(
            self._astonomy_data_file, 
            "astronomy/point", 
            spot, 
            time_span)

        return self._prepare_astronomy_data(raw_data)

    def _prepare_astronomy_data(self, raw_data):
        return list(map(lambda d: Astronomy(
            time=arrow.get(d["time"]),
            sunrise=_maybe_time(d, "sunrise"),
            sunset=_maybe_time(d, "sunset"),
            moonrise=_maybe_time(d, "moonrise"),
            moonset=_maybe_time(d, "moonset"),
            astronomical_dawn=_maybe_time(d, "astronomicalDawn"),
            astronomical_dusk=_maybe_time(d, "astronomicalDusk"),
            nautical_dawn=_maybe_time(d, "nauticalDawn"),
            nautical_dusk=_maybe_time(d, "nauticalDusk"),
            civil_dawn=_maybe_time(d, "civilDawn"),
            civil_dusk=_maybe_time(d, "civilDusk"),
        ), raw_data["data"]))

    def _load_or_fetch_data(self, data_file, endpoint, spot, time_span, **params):
        if self._is_stale(data_file):
            print(f"[Stormglass] fetching {endpoint} data...")
            raw_data = self._fetch_data(endpoint, spot, time_span, **params)
            # cache for reuse
            self._save_data(raw_data, data_file)
        else:
            print(f"[Stormglass] using cached {endpoint} data")
            raw_data = self._load_data(data_file)

        return raw_data

    def _fetch_data(self, endpoint, spot, time_span, **extra_params):
        (time_from, time_to) = time_span
        params = {
            'lat': spot.latitude,
            'lng': spot.longitude,
            'source': 'sg', # automatically choose best source
            'start': time_from.timestamp(),
            'end': time_to.timestamp()
        }
        params.update(extra_params),

        response = requests.get(
          'https://api.stormglass.io/v2/' + endpoint,
          params=params,
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
        if not file_path.exists():
            return True

        modified = arrow.get(file_path.stat().st_mtime)
        now = arrow.now()

        return modified.date() != now.date()


def _maybe_time(data, key):
    t = data.get(key)
    if t is not None:
        return arrow.get(t)
