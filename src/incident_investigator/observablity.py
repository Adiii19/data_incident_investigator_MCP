import logging
from uuid import uuid4

logger=logging.getLogger(__name__)

def create_investigation_id()->str:
    return str(uuid4())