import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SQlAlchemyBase = orm.declarative_base()

__factory__ = None


def global_init(db_file):
    global __factory__
    if __factory__:
        return
    if not db_file or not db_file.strip():
        raise Exception('Необходимо указать имя файла базы данных')
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {db_file}")
    engin = sa.create_engine(conn_str, echo=False)  # echo=True для того, чтобы выводить все запросы в консоль
    __factory__ = orm.sessionmaker(bind=engin)

    from . import __all_models

    SQlAlchemyBase.metadata.create_all(engin)


def create_session() -> Session: # -> значит, что наша функция возвращает конкретный тип(аннотация типа)
    global __factory__
    return __factory__()