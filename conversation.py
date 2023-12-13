import asyncio
import os

from dotenv import load_dotenv

import openai_access
from function_tools import local_functions
from db_access import store
from transitions import Machine, State
from models import XConversation, XMessage, XRunDetail, XRun

from openai.types.beta import Thread
from openai.types.beta.threads import ThreadMessage, Run
import json

from pubsub import pub

load_dotenv()

def start_conversation(asst_id):
    mediator = get_default_mediator()
    user_proxy = UserProxy(mediator)
    asst_proxy = AssistantProxy(mediator, asst_id)
    mediator.set_proxies(asst_proxy, user_proxy)
    return user_proxy

def get_default_mediator():
    type = os.environ["MEDIATOR_TYPE"]
    if type:
        return get_mediator(type)
    return MediatorBasic()

def get_mediator(type):
    match type:
        case "basic" : mediator = MediatorBasic()
        case "stateMachine": mediator = MediatorStateMachine()
        case _: return None

    return mediator

class UserProxy():
    def __init__(self, mediator):
        self.mediator = mediator
        self.user_message = None
        self.asst_message = None

    def send_user_message(self, msg):
        self.asst_message = None
        self.user_message = msg
        self.mediator.set_user_message(self.user_message)

    def set_asst_message(self, asst_msg):
        self.asst_message = asst_msg

    async def get_assistant_message(self):
        while self.asst_message == None:
            await asyncio.sleep(1)
        return self.asst_message

    def execute_tools(self, run_status):
        results = []
        tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
        for tool_call in tool_calls:
            arguments = json.loads(tool_call.function.arguments)
            output = local_functions.execute_function(tool_call.function.name, arguments)
            result = {
                "call_id" : tool_call.id,
                "function_name" : tool_call.function.name,
                "arguments" : arguments,
                "output" : output
            }
            results.append(result)

            store(XRunDetail(run_id=run_status.id, type="execute_tool", tool=tool_call.function.name,
                             input=json.dumps(arguments), output=json.dumps(output)))

        self.mediator.tools_executed(results)

class AssistantProxy():
    def __init__(self, mediator, asst_id):
        self.mediator = mediator
        self.asst_id = asst_id
        self.create_thread()
        self.run_id = None

    def create_thread(self):
        thread: Thread = openai_access.create_thread()
        conv = XConversation(thread_id=thread.id, default_assistant_id=self.asst_id)
        store(conv)
        self.thread_id = thread.id
    def create_message(self, msg):
        thread_message: ThreadMessage = openai_access.create_message( self.thread_id, "user", msg
        )

    def create_run(self):
        run: Run = openai_access.create_run(thread_id=self.thread_id, assistant_id=self.asst_id)
        self.run_id = run.id

    def start_processing(self, user_message):
        self.run_id = None
        self.create_message(user_message)
        self.create_run()
        asyncio.create_task(self.process())

        store(XRun(run_id=self.run_id, thread_id=self.thread_id, assistant_id=self.asst_id))
        store(XRunDetail(run_id=self.run_id, type="submit_user_msg", input=user_message))
        store(XMessage(thread_id=self.thread_id, source="user_proxy", content=user_message))

        self.mediator.started(user_message)

    async def process(self):
        #TODO timeout
        while (True):
            run_status = openai_access.get_run( thread_id=self.thread_id, run_id=self.run_id)
            print(f"run status: {run_status.status}")
            store(XRunDetail(run_id=self.run_id, type="check_run_status", output=run_status.status))

            if run_status.status == 'completed':
                result =  self.retrieve_completed_message()
                self.mediator.assistant_message_retrieved(result)
                break
            elif run_status.status == 'requires_action':
                self.mediator.action_required(run_status)
            elif run_status.status in ['in_progress', 'queued']:
                self.mediator.running(run_status.status)
                await asyncio.sleep(1)
            else:
                raise Exception(f"Non-actionable status: {run_status.status}")

    def retrieve_completed_message(self):
        messages = openai_access.get_thread_messages(thread_id=self.thread_id)
        response = messages.data[0].content[0].text.value
        store(XRunDetail(run_id=self.run_id, type="retrieve_asst_msg", output=response))
        return response

    def submit_tools_output(self, evt):
        tool_outputs = [{"tool_call_id": result["call_id"], "output":json.dumps(result["output"])} for result in evt]
        openai_access.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=self.run_id,
            tool_outputs=tool_outputs
        )

        for result in evt:
            store(XRunDetail(run_id=self.run_id, type="submit_tool_outputs",
                             tool=f"{result['function_name']}-{result['call_id']}", input=result['output']))

        self.mediator.tools_output_submitted(evt);

class MediatorBasic():

    def __init__(self):
        self.state = 'new'

    def set_proxies(self, asst_proxy, user_proxy):
        self.user_proxy = user_proxy
        self.asst_proxy = asst_proxy

    def set_user_message(self, user_message):
        self.state = 'ready'
        self.store_state()
        self.asst_proxy.start_processing(user_message)

    def started(self, user_message):
        self.state = 'started'
        self.store_state()
        pub.sendMessage("sentMessage", evt=f"📡 Sent message, run_id {self.asst_proxy.run_id}: {user_message}")

    def running(self, status):
        self.state = 'active'
        self.store_state()

    def action_required(self, run_status):
        self.state = 'action_required'
        self.store_state()
        self.user_proxy.execute_tools(run_status)

    def tools_executed(self, tool_results):
        self.state = 'tools_executed'
        self.store_state()
        self.asst_proxy.submit_tools_output(tool_results)
        for result in tool_results:
            function_name = result["function_name"]
            arguments = result["arguments"]
            output = json.dumps(result["output"])
            pub.sendMessage("executedTool", evt=f"🔧 {function_name} 🔧 : {arguments} ➡️ {output}")

    def tools_output_submitted(self, evt):
        self.state = 'tools_output_submitted'
        self.store_state()

    def assistant_message_retrieved(self, asst_message):
        self.state = 'completed'
        self.store_state()
        self.user_proxy.set_asst_message(asst_message)
        pub.sendMessage("retrievedMessage", evt="📡 Retrieved message : " + asst_message)

    def store_state(self):
        print(f"**state**: {self.state}")
        run_id = self.asst_proxy.run_id or "TBD"
        store(XRunDetail(run_id=run_id, type="state_change", output=self.state))

class MediatorStateMachine():

    def __init__(self):
        self._subscriptions = []
        self.initiate_state_machine()

    def initiate_state_machine(self):
        states = [
            State(name='new'),
            State(name='ready'),
            State(name='started', on_enter=self.on_started),
            State(name='requires_action'),
            State(name='tools_executed', on_enter=self.on_tools_executed),
            State(name='tools_output_submitted'),
            State(name='completed', on_enter=self.on_completed),
            State(name='active')
        ]

        machine = Machine( model=self, states=states, initial='new', send_event=False)
        transition = machine.add_transition

        # the fastest way through the cycle, no actions
        transition('set_user_message', 'new', 'ready', after='_start_processing')
        transition('started', 'ready', 'started')
        transition('assistant_message_retrieved', 'started', 'completed', after='_receive_asst_message')

        # the fastest way through the cycle, with actions
        transition('action_required', 'started', 'requires_action', after='_execute_tools')
        transition('tools_executed', 'requires_action', 'tools_executed', after='_submit_tools_output')
        transition('tools_output_submitted', 'tools_executed', 'tools_output_submitted')
        transition('assistant_message_retrieved', 'tools_output_submitted', 'completed', after='_receive_asst_message')

        # action after action
        transition('action_required', 'tools_output_submitted', 'requires_action', after='_execute_tools')

        # accomodate for the 'active' state (i.e.'in_progress' and 'queued')
        transition('action_required', 'active', 'requires_action', after='_execute_tools')
        transition('assistant_message_retrieved', 'active', 'completed', after='_receive_asst_message')
        transition('running', 'started', 'active')
        transition('running', 'tools_output_submitted', 'active')
        transition('running', 'active', 'active')

        # restart
        transition('set_user_message', 'completed', 'ready', after='_start_processing')

        for state in states:
            state.on_enter.append(self._store_state)

        self.machine = machine

    def set_proxies(self, asst_proxy, user_proxy):
        self.user_proxy = user_proxy
        self.asst_proxy = asst_proxy

    def _start_processing(self, evt):
        self.asst_proxy.start_processing(evt)

    def _receive_asst_message(self, evt):
        self.user_proxy.set_asst_message(evt)

    def _execute_tools(self, evt):
        self.user_proxy.execute_tools(evt)

    def _submit_tools_output(self, evt):
        self.asst_proxy.submit_tools_output(evt)

    def _store_state(self, *args):
        print(f"**state**: {self.state}")
        run_id = self.asst_proxy.run_id or "TBD"
        store(XRunDetail(run_id=run_id, type="state_change", output=self.state))

    def on_completed(self, asst_message):
        pub.sendMessage("retrievedMessage", evt="📡 Retrieved message : " + asst_message)

    def on_started(self, user_message):
        pub.sendMessage("sentMessage", evt=f"📡 Sent message, run_id {self.asst_proxy.run_id}: {user_message}")

    def on_tools_executed(self, results):
        for result in results:
            function_name = result["function_name"]
            arguments = result["arguments"]
            output = json.dumps(result["output"])
            pub.sendMessage("executedTool", evt=f"🔧 {function_name} 🔧 : {arguments} ➡️ {output}")