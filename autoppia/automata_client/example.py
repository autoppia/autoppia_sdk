import asyncio
from autoppia.automata_client import AutomataClient

async def main():
    try:
        client = AutomataClient(api_key="pk_uql4okogwfm")
        task_id = await client.run_task(
            task="Find alpha token price and market cap for subnet 36.",
            initial_url="https://tao.app"
        )
        print(f"<=== Task started with ID: {task_id} ===>")

        while True:
            await asyncio.sleep(1)
            task_status = await client.get_task_status(task_id)
            if task_status == "completed" or task_status == "failed":
                print(f"<=== Task status: {task_status} ===>")
                break

        task_details = await client.get_task(task_id)
        print(f"<=== Task details: ===>")
        print(task_details)

        screenshots = await client.get_task_screenshots(task_id)
        print(f"<=== Task screenshots length: {len(screenshots)} ===>")

        gif = await client.get_task_gif(task_id)
        print(f"<=== Task gif: {gif[:10]}... ===>")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())