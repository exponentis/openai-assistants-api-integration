import asyncio
import os
import traceback
from typing import MutableMapping
from dotenv import load_dotenv
import streamlit as st
import conversation
from pubsub import pub
from conversation import UserProxy

load_dotenv()

default_assistant_id = os.environ["ASSISTANT_ID"]
def listener1(evt):
    st.chat_message("system").write(evt)
    store_message("system", evt)

def listener2(evt):
    run_details.append(evt)

@st.cache_resource
def initialize():
    store : MutableMapping[str, str] = []
    cache_dict = {
        "chat" : None,
        "thread_id": None
    }
    run_details_ = []
    pub.subscribe(listener=listener1, topicName="executedTool") #s1, ok =

    pub.subscribe(listener=listener2, topicName="sentMessage")
    pub.subscribe(listener=listener2, topicName="error")
    pub.subscribe(listener=listener2, topicName="executedTool")
    pub.subscribe(listener=listener2, topicName="retrievedMessage")
    return [store, cache_dict, run_details_, listener1, listener2]

def store_message(role, content):
    store.append({"role": f"{role}", "content": f"{content}"})

def clear_message_store():
    store.clear()

def clean_up():
    clear_message_store()
    st.session_state.conversation = None
    st.session_state.chat_history = None
    cache["chat"] = None
    cache["thread_id"] = None
    run_details.clear()

async def run():
    sidebar = st.sidebar
    with sidebar:

        #st.header("Start a new conversation")
        asst_id = st.text_input('Assistant ID:', value=default_assistant_id, placeholder="Enter the assistant id", key="asst_id") #, on_change=clean_up

        if st.button("Start", type="secondary", key="start"):
            if asst_id:
                clean_up()
                user_proxy = conversation.start_conversation(asst_id)
                thread_id = user_proxy.mediator.asst_proxy.thread_id
                cache["chat"] = user_proxy
                cache["thread_id"] = thread_id

                st.success('Conversation started!', icon="✅")

    if not asst_id or asst_id =="":
        with sidebar:
            st.info("Please provide an assitant id")
        return

    txt = "Conversation not started"
    if cache["thread_id"] != None:
        txt = cache["thread_id"]

    st.header("💬 " + txt)
    st.caption("Powered by OpenAI Assistants API")

    for msg in store:
        st.chat_message(msg["role"]).write(msg["content"])

    prompt = st.chat_input()
    if not asst_id:
        return

    if asst_id and cache["thread_id"] == None:
        with sidebar:
            st.info("Click 'Start' to start your conversation")
        return

    if prompt:
        run_details.clear()
        store_message("user", prompt)
        st.chat_message("user").write(prompt)

        try:
            ###response = await cache["chat"].send_message_and_retrieve_response(prompt)
            user_proxy : UserProxy = cache["chat"]
            user_proxy.send_user_message(prompt)
            response = await user_proxy.get_assistant_message()
            store_message("assistant", response)
            st.chat_message("assistant").write(response)
        except Exception as e:
            st.chat_message("system").write(e)
            raise

    with sidebar:
        if (len(run_details) > 0):
            st.header("Last run details ")
            for e in run_details:
                st.info(e)


if __name__ == "__main__":
    api_key = os.environ["OPENAI_API_KEY"]
    [store, cache, run_details, listener1, listener2] = initialize()
    try:
        asyncio.run(run())
    except Exception as e:
        print(traceback.format_exc())
