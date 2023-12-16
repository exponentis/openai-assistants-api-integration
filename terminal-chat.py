import conversation
import asyncio
import traceback
import os

async def run():
    asst_id = os.environ["ASSISTANT_ID"]
    user_proxy = conversation.start_conversation(asst_id)
    while (True):
        user_input = input("\nUser: ")
        if (user_input.lower() == "exit"):
            break
        user_proxy.send_user_message(user_input)
        response = await user_proxy.get_assistant_message()
        print("Assistant: ")
        print(response)


if __name__ == '__main__':
    try:
        asyncio.run(run())
    except Exception as e:
        print(traceback.format_exc())