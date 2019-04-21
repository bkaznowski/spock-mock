import unittest

from .user_service import UserService
from src import SpockMock


class TestUserService(unittest.TestCase):

    def setUp(self):
        self.mock_db = SpockMock()
        self.user_service = UserService(database=self.mock_db)

        self.stored_users = {}

        def mock_insert(name):
            self.stored_users[len(self.stored_users) + 1] = name
            return len(self.stored_users), name

        def mock_get(id):
            if id in self.stored_users:
                return id, self.stored_users[id]
            else:
                raise Exception('Not found')

        self.mock_db.insert.mock_return = mock_insert
        self.mock_db.get.mock_return = mock_get

    def test_create_inserts_user_into_database(self):
        user_id, name = self.user_service.create_user('user1')

        1 * self.mock_db.insert.specific('user1')

        self.assertTrue(user_id)
        self.assertEqual('user1', name)

    def test_get_retrieves_user_from_the_database(self):
        user_id, name = self.user_service.create_user('user1')

        found_id, found_name = self.user_service.get_user(user_id)

        1 * self.mock_db.get.specific(user_id)
        self.assertEqual(user_id, found_id)
        self.assertEqual(name, found_name)

    def test_get_raises_exception_if_user_not_found(self):
        self.user_service.create_user('user1')
        self.user_service.create_user('user2')

        with self.assertRaises(Exception) as context:
            self.user_service.get_user(-1)
        self.assertIn('Not found', str(context.exception))

    def test_batch_get_retrieves_users_from_the_database(self):
        first_user_id, first_name = self.user_service.create_user('user1')
        second_user_id, second_name = self.user_service.create_user('user2')

        found_users = self.user_service.batch_get_users([first_user_id, second_user_id])

        (1, 2) * self.mock_db.get.any()

        self.assertEqual(found_users[0], (first_user_id, first_name))
        self.assertEqual(found_users[1], (second_user_id, second_name))

    def test_batch_get_raises_exception_if_user_not_found(self):
        first_user_id, first_name = self.user_service.create_user('user1')
        second_user_id, second_name = self.user_service.create_user('user2')

        with self.assertRaises(Exception) as context:
            self.user_service.batch_get_users([first_user_id, second_user_id, -1])
        self.assertIn('Not found', str(context.exception))

    def test_create_user_fails_if_db_is_down(self):
        def mock_db_failure(*_):
            raise Exception('DB failure')
        self.mock_db.insert.mock_specific(mock_db_failure, "' SELECT -- bad sql injection")

        with self.assertRaises(Exception) as context:
            self.user_service.create_user("' SELECT -- bad sql injection")
        self.assertIn('DB failure', str(context.exception))

        self.user_service.create_user("Valid user name")

    def test_create_user_has_default_user_name(self):
        self.user_service.create_user()
        1 * self.mock_db.insert.specific('Some name')
