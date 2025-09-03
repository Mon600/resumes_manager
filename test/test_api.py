from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_register(async_client: AsyncClient):
    response = await async_client.post('/auth/register', json={
        'first_name': 'Петр',
        'last_name': 'Петров',
        'email': 'example@gmail.com',
        'password': '12345678',
        'password_repeat': '12345678'
    })

    assert response.status_code == 200
    data = response.json()
    assert data['ok'] == True


@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient):
    response = await async_client.get('/auth/user')

    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    assert data['email'] == 'example@gmail.com'


@pytest.mark.asyncio
async def test_create_resume(async_client: AsyncClient):
    response = await async_client.post('/resume/new', json={
        'title': 'test',
        'content': 'Test Test'
    })

    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    assert data['title'] == 'test'
    assert data['content'] == 'Test Test'


@pytest.mark.asyncio
async def test_get_resume(async_client: AsyncClient):
    response = await async_client.get('/resume/1')

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == 1
    assert data['title'] == 'test'


@pytest.mark.asyncio
async def test_get_resume_list(async_client: AsyncClient):
    await async_client.post('/resume/new', json={
        'title': 'test1',
        'content': 'Test Test1',
    })

    response = await async_client.get('/resume/user/1/resumes')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert {r['title'] for r in data} == {'test', 'test1'}