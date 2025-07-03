import asyncio
from autoppia.automata_client import AutomataClient

async def main():
    try:
        client = AutomataClient(api_key="your_api_key")
        task_id = await client.run_task(
            task="Go to hackernews show hn and give me the first 3 posts"
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
        print(f"<=== Task gif: {gif[:50]}... ===>")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())