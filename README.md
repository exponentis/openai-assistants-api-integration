# Resilient OpenAI Assistants API integration

This is a pilot toolkit for a well-designed Python-based integration with OpenAI's Assistants API, built to withstand the 
fast-evolving AI technology landscape. 

## Introduction

The Assistants API allows clients to create customized assistants and run conversations and interactions following a 
sequence of steps, all one-way, from the client to theOpenAI API (see 
[OpenAI Assistants documentation](https://platform.openai.com/assistants). When doing so, it is 
important to follow software engineering best practices, to make sure our systems are future-ready for the rapid 
advancements in the AI technology field. The main ideas behind this toolkit design are:

1. Our AI-powered business use cases and flows run in our local systems, interacting with external AI services, such as 
OpenAI's Assistants API, and we need to maintain an **end-to-end perspective** when implementing integrations with such 
external systems.


2. The conversation between the client system and the Assistants API follows a **pre-defined interaction script**, modeled as a 
**state machine**. The main actors are a **User/Client Proxy** and an **Assistant Proxy**, interacting indirectly via a **Mediator** that is 
implemented (formally or informally) as a state machine.


3. All calls to the Assistants API fall under the **responsibility of the Asistant Proxy, who acts as an active player 
in the client eco-system**, detecting changes  on the remote Assistant side and interacting directly with the conversation 
Mediator, and indirectly with the User Proxy.


4. **The User Proxy acts on behalf of the user and the system** is reponsible for interacting (indirectly) with the Assistant Proxy on, 
passing messages from the User and making internal calls as needed (such as executing function tools registered with the 
assistant).

## Dependencies

Python 3.x (developed with 3.11)

streamlit~=1.29.0

pydantic~=2.5.2

Pypubsub~=4.0.3

SQLAlchemy~=2.0.23

pandas~=2.1.4

openai~=1.3.8

yfinance~=0.2.33

transitions~=0.9.0

python-dotenv~=1.0.0

## Setup

### Code and virtual environment
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

Run assistant_setup.py to create the sample assitant:

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




