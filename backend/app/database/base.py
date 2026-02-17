from sqlalchemy.orm import declarativebase

class Base(declarativebase):
    pass

from models.user import User