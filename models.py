from sqlalchemy.orm import registry

import database

class XAssistant:
    pass

class XConversation:
    pass

class XRun:
    pass

class XMessage:
    pass

class XRunDetail:
    pass

mapper_registry = registry()

mapper_registry.map_imperatively(XConversation, database.conversations)
mapper_registry.map_imperatively(XMessage, database.conversation_messages)
mapper_registry.map_imperatively(XRun, database.conversation_runs)
mapper_registry.map_imperatively(XRunDetail, database.run_details)