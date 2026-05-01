from homeassistant.components import websocket_api

from custom_components.saviia.const import GeneralParams


@websocket_api.websocket_command({"type": "saviia/get_people"})
@websocket_api.async_response
async def ws_get_people(hass, connection, msg) -> None:
    domain_data = hass.data.get(GeneralParams.DOMAIN, {})
    for entry_id in domain_data:
        if entry_id in {"services_registered", "websocket_registered"}:
            continue

        storage = domain_data[entry_id].get("storage")
        if storage is None:
            continue

        people = await storage.async_get_people()
        connection.send_result(msg["id"], people)
        return

    connection.send_result(msg["id"], [])
