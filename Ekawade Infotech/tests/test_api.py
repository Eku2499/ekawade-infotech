import os
import tempfile
import json
import pytest
from booking_api import app, init_db, DB_FILE

@pytest.fixture
def client(tmp_path, monkeypatch):
    # use a temporary DB file for tests
    tmpdb = tmp_path / 'test_bookings.db'
    monkeypatch.setenv('BOOKING_DB', str(tmpdb))
    init_db(migrate_from_excel=False)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_post_and_get(client):
    # post a booking
    rv = client.post('/book', json={'name':'T1','email':'t1@example.com','date':'2025-10-20','phone':'900'})
    assert rv.status_code == 200
    assert rv.json['status'] == 'success'

    # get bookings
    rv = client.get('/bookings')
    assert rv.status_code == 200
    data = rv.json
    assert 'bookings' in data
    assert data['total'] == 1

def test_delete(client):
    rv = client.post('/book', json={'name':'T2','email':'t2@example.com','date':'2025-10-21','phone':'901'})
    assert rv.status_code == 200
    # fetch id
    rv = client.get('/bookings')
    bid = rv.json['bookings'][0]['id']
    rv = client.delete(f'/bookings/{bid}')
    assert rv.status_code == 200
    assert rv.json['status'] == 'success'

def test_export(client):
    client.post('/book', json={'name':'T3','email':'t3@example.com','date':'2025-10-22','phone':'902'})
    rv = client.get('/export')
    assert rv.status_code == 200
    assert rv.data.startswith(b'id,name,email')
