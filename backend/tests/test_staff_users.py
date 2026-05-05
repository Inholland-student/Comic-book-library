"""POST /api/auth/users — super_admin vs admin rules (needs mysql + seed super_admin)."""
import pytest
from datetime import datetime


def _uniq(prefix):
    return f"{prefix}_{datetime.now().timestamp()}".replace('.', '_')


def test_users_endpoint_requires_auth(client):
    u = _uniq('x')
    r = client.post(
        '/api/auth/users',
        json={
            'username': u,
            'email': f'{u}@t.local',
            'password': 'abc12345',
            'role': 'admin',
        },
    )
    assert r.status_code == 401


def test_super_admin_can_create_friend(client):
    login = client.post(
        '/api/auth/login',
        json={'username': 'super_admin', 'password': 'changeme'},
    )
    assert login.status_code == 200
    u = _uniq('friendfromsuper')
    r = client.post(
        '/api/auth/users',
        json={
            'username': u,
            'email': f'{u}@t.local',
            'password': 'abc12345',
            'role': 'friend',
        },
    )
    assert r.status_code == 201
    assert r.get_json()['role'] == 'friend'


def test_super_admin_creates_admin(client):
    login = client.post(
        '/api/auth/login',
        json={'username': 'super_admin', 'password': 'changeme'},
    )
    assert login.status_code == 200
    u = _uniq('newadm')
    r = client.post(
        '/api/auth/users',
        json={
            'username': u,
            'email': f'{u}@t.local',
            'password': 'abc12345',
            'role': 'admin',
        },
    )
    assert r.status_code == 201
    assert r.get_json()['role'] == 'admin'


def test_friend_gets_403(client):
    u = _uniq('friendonly')
    reg = client.post(
        '/api/auth/register',
        json={
            'username': u,
            'email': f'{u}@t.local',
            'password': 'abc12345',
        },
    )
    assert reg.status_code == 201
    inn = client.post(
        '/api/auth/login',
        json={'username': u, 'password': 'abc12345'},
    )
    assert inn.status_code == 200
    u2 = _uniq('nope')
    r = client.post(
        '/api/auth/users',
        json={
            'username': u2,
            'email': f'{u2}@t.local',
            'password': 'abc12345',
            'role': 'admin',
        },
    )
    assert r.status_code == 403


def test_admin_can_create_friend(client):
    login = client.post(
        '/api/auth/login',
        json={'username': 'admin_user', 'password': 'changeme'},
    )
    assert login.status_code == 200
    u = _uniq('fromadmin')
    r = client.post(
        '/api/auth/users',
        json={
            'username': u,
            'email': f'{u}@t.local',
            'password': 'abc12345',
            'role': 'friend',
        },
    )
    assert r.status_code == 201
    assert r.get_json()['role'] == 'friend'


def test_admin_rejects_admin_role(client):
    login = client.post(
        '/api/auth/login',
        json={'username': 'admin_user', 'password': 'changeme'},
    )
    assert login.status_code == 200
    u = _uniq('admincant')
    r = client.post(
        '/api/auth/users',
        json={
            'username': u,
            'email': f'{u}@t.local',
            'password': 'abc12345',
            'role': 'admin',
        },
    )
    assert r.status_code == 400
