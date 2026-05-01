from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

STORAGE_VERSION = 1
STORAGE_KEY = "saviia_data"


def _default_data() -> dict[str, list[Any]]:
    return {"people": [], "tasks": []}


class SaviiaStorage:
    def __init__(self, hass: HomeAssistant, entry_id: str):
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry_id}")
        self._data: dict[str, list[Any]] | None = None

    async def async_load(self) -> dict[str, list[Any]]:
        if self._data is None:
            self._data = await self._store.async_load()
            if self._data is None:
                self._data = _default_data()
        return self._data

    async def async_save(self) -> None:
        await self._store.async_save(self._data)

    async def async_get_people(self) -> list[Any]:
        data = await self.async_load()
        return data["people"]

    async def async_add_person(self, person) -> None:
        data = await self.async_load()
        data["people"].append(person)
        await self.async_save()

    async def async_delete_person(self, person_id) -> None:
        data = await self.async_load()
        data["people"] = [p for p in data["people"] if p["id"] != person_id]
        await self.async_save()
