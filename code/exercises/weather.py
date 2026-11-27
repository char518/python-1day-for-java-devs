import asyncio

import httpx


def fetch_temp(city: str) -> str:
    r = httpx.get(f"https://wttr.in/{city}?format=j1", timeout=10)
    r.raise_for_status()
    return r.json()["current_condition"][0]["temp_C"]


async def fetch_temp_async(client: httpx.AsyncClient, city: str) -> str:
    r = await client.get(f"https://wttr.in/{city}?format=j1")
    r.raise_for_status()
    return r.json()["current_condition"][0]["temp_C"]


async def main():
    async with httpx.AsyncClient(timeout=10) as client:
        temps = await asyncio.gather(
            fetch_temp_async(client, "Beijing"),
            fetch_temp_async(client, "Shanghai"),
        )
    print("Beijing/Shanghai:", temps)


if __name__ == "__main__":
    print("Beijing:", fetch_temp("Beijing"))
    asyncio.run(main())