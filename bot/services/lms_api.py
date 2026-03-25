"""LMS API client for communicating with the backend."""

import httpx
from typing import Optional


class LmsApiService:
    """Service for making HTTP requests to the LMS backend."""

    def __init__(self, base_url: str, api_key: str):
        """Initialize the API client.

        Args:
            base_url: Base URL of the LMS API (e.g., http://localhost:42002).
            api_key: API key for Bearer token authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def get_items(self) -> Optional[list]:
        """Fetch all items (labs and tasks) from the backend.

        Returns:
            List of items, or None if the request fails.
        """
        try:
            response = self._client.get("/items/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise LmsApiError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.ConnectError as e:
            raise LmsApiError(f"connection refused ({self.base_url}). Check that the services are running.")
        except httpx.TimeoutException as e:
            raise LmsApiError("request timed out. The backend may be overloaded.")
        except Exception as e:
            raise LmsApiError(f"unexpected error: {str(e)}")

    def get_pass_rates(self, lab: str) -> Optional[list]:
        """Fetch pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            List of pass rate data, or None if the request fails.
        """
        try:
            response = self._client.get("/analytics/pass-rates", params={"lab": lab})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise LmsApiError(f"lab '{lab}' not found.")
            raise LmsApiError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.ConnectError as e:
            raise LmsApiError(f"connection refused ({self.base_url}). Check that the services are running.")
        except httpx.TimeoutException as e:
            raise LmsApiError("request timed out. The backend may be overloaded.")
        except Exception as e:
            raise LmsApiError(f"unexpected error: {str(e)}")

    def health_check(self) -> dict:
        """Check if the backend is healthy.

        Returns:
            Dict with 'healthy' boolean and 'item_count' if healthy.

        Raises:
            LmsApiError: If the backend is unhealthy or unreachable.
        """
        try:
            response = self._client.get("/items/")
            response.raise_for_status()
            items = response.json()
            return {"healthy": True, "item_count": len(items)}
        except httpx.HTTPStatusError as e:
            raise LmsApiError(f"HTTP {e.response.status_code} Bad Gateway. The backend service may be down.")
        except httpx.ConnectError as e:
            raise LmsApiError(f"connection refused ({self.base_url}). Check that the services are running.")
        except httpx.TimeoutException as e:
            raise LmsApiError("request timed out. The backend may be overloaded.")
        except Exception as e:
            raise LmsApiError(f"unexpected error: {str(e)}")


class LmsApiError(Exception):
    """Custom exception for LMS API errors."""

    pass
