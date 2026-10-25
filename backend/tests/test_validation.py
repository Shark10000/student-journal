import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db

@pytest.fixture
def client():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    @event.listens_for(engine, 'connect')
    def foreign_keys(conn, _):
        conn.execute('PRAGMA foreign_keys=ON')
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    def override():
        with session() as db:
            yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()


def student(client, **kwargs):
    return client.post('/api/students', json={'full_name':'Анна Смирнова', 'group':'ПИ-21', 'email':'anna@example.com', **kwargs})


@pytest.mark.parametrize('patch',[{'full_name':' '},{'email':'bad'},{'group':''},{'unknown':1}])
def test_invalid_student(client,patch):
    assert student(client,**patch).status_code==422


@pytest.mark.parametrize('patch',[{'value':1},{'value':6},{'value':4.5},{'value':True},{'subject':' '},{'date':'not-a-date'}])
def test_invalid_grade(client,patch):
    sid=student(client).json()['id']
    assert client.post(f'/api/students/{sid}/grades',json={'subject':'Физика','value':5,**patch}).status_code==422


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"sort": "password"}, {"order": "invalid"}])
def test_invalid_query_parameters(client, params):
    assert client.get('/api/students', params=params).status_code == 422
