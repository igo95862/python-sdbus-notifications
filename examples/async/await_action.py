# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 igo95862
from __future__ import annotations

from asyncio import FIRST_COMPLETED, get_running_loop
from asyncio import run as asyncio_run
from asyncio import wait

from sdbus_async.notifications import FreedesktopNotifications

# FreedesktopNotifications is a class that automatically proxies to
# the notifications daemon's service name and path.
# NotificationsInterface is the raw interface that can be used to
# implement your own daemon or proxied to non-standard path.


async def wait_action_invoked(
    notifications: FreedesktopNotifications,
    notifications_waiting: set[int],
) -> None:
    async for (
        notification_id,
        action_key,
    ) in notifications.action_invoked.catch():
        if notification_id in notifications_waiting:
            print("Action invoked:", action_key)
            return


async def wait_notification_closed(
    notifications: FreedesktopNotifications,
    notifications_waiting: set[int],
) -> None:
    async for (
        notification_id,
        reason,
    ) in notifications.notification_closed.catch():
        if notification_id in notifications_waiting:
            print("Notification closed!")
            return


async def main() -> None:
    # Default bus will be used if no bus is explicitly passed.
    # When running as user the default bus will be session bus where
    # Notifications daemon usually runs.
    notifications = FreedesktopNotifications()
    notifications_waiting: set[int] = set()

    loop = get_running_loop()

    # Always bind tasks to variables or they will be garbage collected
    action_invoked_task = loop.create_task(
        wait_action_invoked(
            notifications,
            notifications_waiting,
        )
    )
    notification_closed_task = loop.create_task(
        wait_notification_closed(
            notifications,
            notifications_waiting,
        )
    )

    notification_id = await notifications.notify(
        # summary is the only required argument.
        # For other arguments default values will be used.
        summary="Foo or Bar?",
        body="Select either Foo or Bar.",
        # Actions are defined in pairs of action_key to displayed string.
        actions=["foo", "Foo", "bar", "Bar"],
    )
    notifications_waiting.add(notification_id)

    await wait(
        (action_invoked_task, notification_closed_task),
        return_when=FIRST_COMPLETED,
    )


if __name__ == "__main__":
    asyncio_run(main())