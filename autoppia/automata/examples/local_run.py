import asyncio
from autoppia.automata import AutomataAgent

async def main():
    try:
        agent = AutomataAgent(api_key="your_api_key")
        result = await agent.run_locally(
            task="Go to hackernews show hn and give me the first 3 posts",
            user_data_dir="C:\\Users\\YourUser\\AppData\\Local\\Google\\Chrome\\User Data\\Default",
            chrome_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        )
        print(result)
        await agent.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())