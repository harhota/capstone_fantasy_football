"""FPL API client with robust HTTP handling and retries."""

from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class FPLClient:
    """Lightweight client for the Fantasy Premier League API."""

    BASE_URL = "https://fantasy.premierleague.com/api/"

    def __init__(self, session: requests.Session | None = None, *, retries: int = 3,
                 backoff_factor: float = 0.3,
                 status_forcelist: tuple[int, ...] = (500, 502, 503, 504)) -> None:
        self.session = session or requests.Session()

        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=frozenset(["GET"]),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get(self, endpoint: str) -> dict:
        url = urljoin(self.BASE_URL, endpoint)
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:  # noqa: PERF203
            raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc

    def get_bootstrap_static(self) -> dict:
        """Return the main static bootstrap data."""
        return self._get("bootstrap-static/")