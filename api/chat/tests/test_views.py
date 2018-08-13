import pytest

from api.chat.models import Room
from api.chat.tests.utils import LoginableTestCase


@pytest.mark.django_db
class TestUserView(LoginableTestCase):
    def test_register(self):
        data = {
            'username': '001',
            'password': '001',
        }
        res = self.client.post('/v1/users/', data=data)
        assert res.status_code == 201
    def test_register_fail_no_password(self):
        data = {
            'username': '001',
        }
        res = self.client.post('/v1/users/', data=data)
        assert res.status_code == 400

    def test_register_fail_no_username(self):
        data = {
            'password': '001',
        }
        res = self.client.post('/v1/users/', data=data)
        assert res.status_code == 400

    def test_register_fail_exist_username(self, users):
        data = {
            'username': '001',
            'password': '001',
        }
        res = self.client.post('/v1/users/', data=data)
        assert res.status_code == 400

    def test_my_detail(self, users):
        res = self.client.get('/v1/users/1/')
        assert res.status_code == 401
        self.login('001', '001')
        res = self.client.get('/v1/users/1/')
        assert res.status_code == 200

    def test_not_my_detail(self, users):
        self.login('001', '001')
        res = self.client.get('/v1/users/2/')
        assert res.status_code == 404
        res = self.client.delete('/v1/users/2/')
        assert res.status_code == 404


@pytest.mark.django_db
class TestRoomView(LoginableTestCase):
    def test_room_list_without_data(self, users):
        self.login('001', '001')
        res = self.client.get('/v1/rooms/')
        assert res.status_code == 200
        assert res.data == []

    def test_room_list_with_data(self, room):
        self.login('001', '001')
        res = self.client.get('/v1/rooms/')
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1

        room = data[0]
        assert room['id'] == 1
        assert room['title'] == 'test001'
        assert len(room['participants']) == 2
        assert room['participants'][0] == 1
        assert room['participants'][1] == 2

    def test_room_detail(self, room):
        self.login('001', '001')
        res = self.client.get('/v1/rooms/1/')
        assert res.status_code == 200
        data = res.json()
        assert data['id'] == 1
        assert data['title'] == 'test001'
        assert len(data['participants']) == 2
        assert data['participants'][0] == 1
        assert data['participants'][1] == 2

    def test_room_detail_non_exist(self, users):
        self.login('001', '001')
        res = self.client.get('/v1/rooms/1/')
        assert res.status_code == 404

    def test_not_my_room(self, another_user, room):
        self.login('003', '003')
        res = self.client.get('/v1/rooms/')
        assert res.status_code == 200
        assert res.data == []
        res = self.client.get('/v1/rooms/1/')
        assert res.status_code == 404

        self.login('001', '001')
        res = self.client.get('/v1/rooms/')
        assert res.data != []

    def test_our_room(self, room):
        self.login('001', '001')
        res = self.client.get('/v1/rooms/')
        rooms_of_001 = res.data
        self.login('002', '002')
        res = self.client.get('/v1/rooms/')
        rooms_of_002 = res.data
        assert rooms_of_001 == rooms_of_002


@pytest.mark.django_db
class TestMessageView(LoginableTestCase):
    def test_msg_list_without_data(self, room):
        self.login('001', '001')
        res = self.client.get('/v1/rooms/1/messages/')
        assert res.status_code == 200
        data = res.json()
        assert data == []

    def test_msg_list_with_data(self, room, msg):
        self.login('001', '001')
        res = self.client.get('/v1/rooms/1/messages/')
        assert res.status_code == 200
        data = res.data
        assert len(data) == 1
        msg = data[0]
        assert msg['id'] == 1
        assert msg['sender'] == 1
        assert msg['content'] == 'hello'

    def test_not_my_messages(self, another_user, room, conversation):
        self.login('003', '003')
        res = self.client.get('/v1/rooms/1/messages/')
        assert res.status_code == 404

        self.login('001', '001')
        res = self.client.get('/v1/rooms/1/messages/')
        assert len(res.data) == 6

    def test_our_messages(self, room, conversation):
        self.login('001', '001')
        res = self.client.get('/v1/rooms/1/messages/')
        msgs_of_001 = res.data
        self.login('002', '002')
        res = self.client.get('/v1/rooms/1/messages/')
        msgs_of_002 = res.data
        assert msgs_of_001 == msgs_of_002