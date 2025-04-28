import logging
import uuid
from typing import Any, Union

from fast_depends import Depends, inject
from socketio import AsyncManager, AsyncServer

from logic import TypedContainer, init_container

logger = logging.getLogger(__name__)

UserOID = str


@inject
async def _authenticate(
    headers: dict[str, Any], container: TypedContainer = Depends(init_container)
) -> UserOID:
    """
    Authenticates the user based on the provided headers.

    This function generates a unique user identifier (OID) for each new connection.
    The OID is then used for session management and room subscription.

    :param headers: A dictionary of headers associated with the connection.
    :type headers: dict[str, Any]

    :param container: A container for resolving dependencies.
    :type container: TypedContainer

    :return: A unique user identifier (OID) for the authenticated user.
    :rtype: UserOID
    """
    user_oid = str(uuid.uuid4())
    return user_oid


@inject
def create_asgi_sio(container: TypedContainer = Depends(init_container)) -> AsyncServer:
    """
    Creates and initializes the Socket.IO ASGI server.

    This function resolves the `AsyncManager` from the container and creates
    an instance of `AsyncServer` for managing real-time events.

    :param container: A container for resolving dependencies.
    :type container: TypedContainer

    :return: An instance of the `AsyncServer` for handling Socket.IO connections.
    :rtype: AsyncServer
    """
    mgr = container.resolve(AsyncManager)
    sio = AsyncServer(async_mode="asgi", cors_allowed_origins="*", client_manager=mgr)
    return sio


sio = create_asgi_sio()


@sio.event  # type: ignore
async def connect(
    sid: str,
    environ: dict[str, Any],
) -> bool:
    """
    Handles a new user connection to the server.

    This function authenticates the user, generates a unique user OID, and
    saves the session to associate the user with the given Socket.IO session ID (sid).

    :param sid: The Socket.IO session ID of the connecting user.
    :type sid: str

    :param environ: The environment variables for the current connection request.
    :type environ: dict[str, Any]

    :return: A boolean indicating if the connection is successful.
    :rtype: bool
    """
    user_oid = await _authenticate(environ)
    await sio.save_session(sid, {"user_oid": user_oid})
    logger.info(f"[+] User {user_oid} connected with sid {sid}")
    return True


@sio.event  # type: ignore
async def sub_to_notifications(
    sid: str, data: Any = None
) -> Union[tuple[str, str, list[str]], None]:
    """
    Subscribes a user to notifications and adds them to the appropriate rooms.

    This function checks if the user is authorized by verifying their session.
    If authorized, the user is subscribed to specific rooms for receiving notifications.

    :param sid: The Socket.IO session ID of the user requesting the subscription.
    :type sid: str

    :param data: Optional data passed along with the subscription request.
    :type data: Any, optional

    :return: A tuple containing the response status, user OID,
             and rooms the user is subscribed to.
    :rtype: tuple[str, str, list[str]] | None
    :raises: None
    """
    session: dict[str, Any] = await sio.get_session(sid)
    user_oid = session.get("user_oid")
    if not user_oid:
        logger.warning(f"Unauthorized sub attempt from {sid}")
        await sio.disconnect(sid)
        return None

    rooms = ["system", user_oid]
    for room in rooms:
        await sio.enter_room(sid, room)

    return "OK", user_oid, rooms


@sio.event  # type: ignore
async def disconnect(sid: str) -> None:
    """
    Handles a user disconnection from the server.

    This function logs the disconnection event and can be extended to handle
    any necessary cleanup operations when a user disconnects.

    :param sid: The Socket.IO session ID of the disconnected user.
    :type sid: str

    :return: None
    :rtype: None
    """
    logger.info(f"[-] Client disconnected: {sid}")
