from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


# Database (aio SQLite3)
engine = create_async_engine('sqlite+aiosqlite:///bot_db.db', echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)