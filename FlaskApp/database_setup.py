from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__= 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), unique=True, nullable=False, index=True)
    author = Column(String(350))
    genre = Column(String(50))
    format = Column(String(50))
    image = Column(String(250))
    num_pages = Column(Integer)
    pub_date = Column(String(20))
    pub_name = Column(String(80))
    pub_id = Column(String(10))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in serializeable format"""
        return {
            'id' : self.id,
            'title' : self.title,
            'author' : self.author,
            'genre' : self.genre,
            'format' : self.format,
            'image' : self.image,
            'num_pages' : self.num_pages,
            'pub_date' : self.pub_date,
            'pub_name' : self.pub_name,
        }

engine = create_engine('postgresql://catalog:catalog@localhost/bookcatalog')

Base.metadata.create_all(engine)
