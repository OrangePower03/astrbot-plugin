# https://github.com/OrangePower03/astrbot-plugin

import asyncio
import time

import websockets


async def simple_example():
    while True:
        async with websockets.connect("ws://localhost:8081/bot") as ws:
            response = await ws.recv()
            print(f"Received: {response}")

asyncio.run(simple_example())
time.sleep(1000)

