# OpenAI Assistants API Integration toolkit

This is a pilot toolkit for a well-designed, resilient Python-based integration with OpenAI's Assistants API, built to withstand the fast-evolving AI technology landscape. The deisgn can be used for other similar API integrations as well.

## Introduction

The Assistants API allows clients to create customized assistants and run complex conversations following a 
sequence of steps (see [OpenAI Assistants documentation](https://platform.openai.com/assistants). The interactions are one-way, from the client to theOpenAI API, as OpenAI does not make call-backs or send notifications. When building integrations with the Assistants API, it is important to follow software engineering best practices, to make sure our systems are future-ready for the rapid advancements in the AI technology field. 

Here are the main ideas behind the design of this toolkit:

1. Maintain an **end-to-end perspective** of the flows that have assistants as particpants; the integration with the external API is just one piece of the puzzle. One will need full visibility into the execution of the end-to-end AI-powered workflows.


2. The conversation between the client system and the Assistants API follows a **pre-defined interaction script**, modeled as a **state machine**. The main actors are a **User Proxy** and an **Assistant Proxy**, interacting indirectly under the supervision of a **Mediator** who owns the interaction script.


3. The **Assistant Proxy** acts on behalf of the Assistant, exclusively managing the calls to the Assistants API, and interacting indirectly with the User Proxy via the Mediator. 


4. **The User Proxy** acts on behalf of the user and other internal systems that require Assistants API integration, interacting indirectly with the Assistant Proxy via the Mediator and making supporting internal calls as needed (such as executing function tools registered with the assistant when instructed so by the Assistant, via the Mediator).

## Design

The diagram below shows how the User Proxy, Assistant Proxy and Mediator work together within the overall tech ecosystem to implement a clean integration with the Assistants API:

![Arch](diagrams/arch.svg)

The Assistant Proxy makes regular calls to the Assistants API to check on the Run status (polling), and processes the return status accordingly, with the help of the Mediator. The User Proxy initiates a conversation exchange through a prompt, and assists with function calls as needed.

As mentioned earlier, the Mediator is implemented (formally or informally) as a state machine, with transitions as shown below:

![State](diagrams/state.svg)

The states are based on:

1. the external Assistant's Run status
2. the status of supporting internal calls, related to executing required actions

and provide a perspective of the overall execution rathar than just the Assistant's progress.

The dotted-line transitions are allowed in case the "running" state is missed when polling the Assisstans API (which can happen when processing is faster than the polling interval, or when polling is delayed, like it may happen when the app is running in debug mode with break points)

The sequence diagram below shows the detailed interaction script during a conversation exchange:

![Sequence](diagrams/seq.svg)

## Implementation Details

### User Proxy

### Assistants Proxy

### Mediator
There are two implementations for the Mediator:

- MediatorBasic, a plain Python implementation, that does not enforce pre-conditions for state transitions
- MediatorStateMachine, with all bells and whistle, using [transition](https://github.com/pytransitions/transitions), an excellent state machine implementation in Python.

## User Interface

Using the integration toolkit, one can build user interfaces with ease, through a clean integration with the User Proxy and optionally listen to events emotted by the Mediator. The sample streamlit-based UI allows users to start conversations with an assistant that is configured with 2 functions as tools, and function calls are displayed real time as part of the chat window. See screenhot below:

![Chat](screenshots/chat.png)

In addition, there is a second streamlit page that shows the conversation history and useful logs (including function calls, and even polling). It also uses [Link] aggrid. See screenhot below:

![HistoryChat](screenshots/hist.png)

## Dependencies

Python 3.x (developed with 3.11)

streamlit~=1.29.0

streamlit-aggrid~=0.3.4

pydantic~=2.5.2

Pypubsub~=4.0.3

SQLAlchemy~=2.0.23

pandas~=2.1.4

openai~=1.3.8

yfinance~=0.2.33

transitions~=0.9.0

python-dotenv~=1.0.0

## Setup

### Code and dependencies

Clone this repository and use your favorite IDE to open it as a project:

```bash
git clone https://github.com/exponentis/openai-assistants-api-integration.git
```

Create a virtual environment, activate it and install dependencies:

```bash
cd openai-assistants-api-integration
pip install -r requirements.txt
```

### Configuration

Copy the coontents of the file `.env_sample` to a new file named `.env` and update the `OPEN_API_KEY` variable (see 
[https://platform.openai.com/api-keys](https://platform.openai.com/api-keys))

### Assistant

Run assistant_setup.py to create the sample assisßtant:

```python
python assistant_setup.py
```
Capture the assistent ID (either from your OpenAI gpt+ account, or from the terminal after running the above script) and 
update the `ASSISTANT_ID` variable in the `.env' file

### Database

The project uses sqlite with a folder called `dbstorage` for storage. Run the db_setup.py script to create the database 
and the schema:

```python
python db_setup.py
```

## Running the app

Open the chat page to start conversations with assistants by running:

```python
streamlit run streamlit-chat.py
```

The page loads the Assistant ID from `.env` as default; it can be overriden before starting a new 
conversation.

To open the history page and browse data stored in the database, run:

```python
streamlit run streamlit-history.py
```




