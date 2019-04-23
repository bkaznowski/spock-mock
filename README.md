# SpockMock

## Introduction
I have recently started writing a lot of Python code and so I have to mock a lot of objects in Python for unit testing.
While writing these tests I quickly discovered how painful it was to mock objects using the standard Python `unittest.Mock`.
You get used to it after a while but I thought that there must be a better way.
I knew that mocking could be greatly improved upon, as one of the previous projects I was working on used a testing framework for JVM based languages called [Spock](http://spockframework.org/).
I found that the tests written in the Spock testing framework were easy to write and very easy to read. One of the most impressive parts of the Spock testing framework is how easy it is to mock objects and work with mocked objects.
This library allows Spock-like mocking features to be used in the standard Python testing framework.

## Should you be using this?
If you want a nicer method for mocking objects in Python, then please do!

One of the main reasons why I believe this is better than normal Python mocking is that it allows you to abstract the specific method implementation away by implementing mock objects to replicate how the real objects would work in an easy way.
You can then reuse these mocks in all your tests and only mock specific cases when necessary.

Bear in mind though that this is not being used in production anywhere, so it may not be fully production ready.
If you do plan to use this, then let me know and I will try and get it to production quality. Please also let me know of any bugs or feature requests.

## Features
- The `SpockMock` class extends from the standard `unittest.Mock`, so you can still use all the functions that the built-in Python mocking class has.
- You can assign mocked methods to mocked objects easily, allowing more flexibility
- You can quickly assert how many times a method was called with any arguments in an intuitive way which is very similar to Spock
- You can quickly assert how many times a method was called with specific arguments in an intuitive way which is very similar to Spock
- You can mock a method to return a value for a specific input. Any other calls with different input will use the base mock unless also mocked for a specific argument.

## Basic Examples

### Mocking a method with a mock implementation
```python
spock_mock_object = SpockMock()
def mock_add_numbers(first_number, second_number):
    return first_number + second_number
spock_mock_object.add_numbers.mock_return = mock_add_numbers

# This will call the provided method and print 3
print(spock_mock_object.add_numbers(1, 2))

# This will call the provided method and print 6
print(spock_mock_object.add_numbers(3, second_number=3))

# This will call the provided method and print 9
print(spock_mock_object.add_numbers(first_number=4, second_number=5))

# This will fail, as the second argument isn't provided
print(spock_mock_object.add_numbers(4))
```

### Mocking a method with a constant
```python
spock_mock_object = SpockMock()
spock_mock_object.get_constant.mock_return = 5

# This will return the base mock and print 5
print(spock_mock_object.get_constant(1, 2))

# This will return the base mock and print 5
print(spock_mock_object.get_constant())
```

### Mocking a method for specific input
```python
spock_mock_object = SpockMock()

def mock_add_numbers(first_number, second_number):
    return first_number + second_number
spock_mock_object.add_numbers.mock_specific(mock_add_numbers, 1, 2)

# This will call the provided method and print 3
print(spock_mock_object.add_numbers(1, 2))

# This won't call the provided method and instead will call the base mock,
# which happens to return a SpockMock object, just like unittest.Mock
print(spock_mock_object.add_numbers(3, second_number=3))

spock_mock_object.add_numbers.specific_mock_return(17, 3, 4)

# This will print 17.
print(spock_mock_object.add_numbers(3, 4))

# Adding a base mock maintains the previously mocked calls
def mock_sub_numbers(first_number, second_number):
    return first_number - second_number
spock_mock_object.add_numbers.mock_return = mock_sub_numbers

# This will print:
# -1, as the base mock was called
# 3, as the specific mock was called
# -1, as the base mock was called
# 17, as the specific mock was called
# -1, as the base mock was called
for i in range(5):
    print(spock_mock_object.add_numbers(i, i + 1))
```

### Asserting specific number of calls
```python
spock_mock_object = SpockMock()
spock_mock_object.some_method(1, 2)
spock_mock_object.some_method()

# Asserts there were 2 calls. This ignores arguments in the calls
2 * spock_mock_object.some_method.any()

# Asserts it was called once with no arguments
1 * spock_mock_object.some_method.specific()

# Assert it was called once with (1, 2) as arguments
1 * spock_mock_object.some_method.specific(1, 2)
```
One thing you might be worried about is linters picking up on the multiplication not being used. This should not be an issue, as the method call should stop linters from reporting this as an unused multiplication.

### Asserting specific range for number of calls
You can also assert the number of calls to a method is within a specific range.
```python
spock_mock_object = SpockMock()
spock_mock_object.some_method(1, 2)
spock_mock_object.some_method()

# Asserts that the method was called between 1 and 3 times (inclusive)
(1, 3) * spock_mock_object.some_method.any()

# This will fail, as there are no calls to some_other_method
(1, 3) * spock_mock_object.some_other_method.any()

spock_mock_object.some_method()
spock_mock_object.some_method()

# This will now fail, as there are 4 calls to some_method
(1, 3) * spock_mock_object.some_method.any()
```
This is useful for when you don't know exactly how many calls there will be.

Say you have a class like `SomeClass` defined below.
You could test it like this:
```python
import unittest
from random import shuffle

from src import SpockMock


class SomeClass:
    def __init__(self, some_object):
        self.some_object = some_object

    def my_method(self):
        some_list = [1, 2, 3]
        shuffle(some_list)
        for i in some_list:
            self.some_object.some_method(i)


class TestSomeClass(unittest.TestCase):
    def test_my_method(self):
        def some_method(num):
            if num == 1:
                raise Exception('Failure')
        spock_mock_object = SpockMock()
        spock_mock_object.some_method.mock_return = some_method
        
        my_class = SomeClass(spock_mock_object)
        with self.assertRaises(Exception) as context:
            my_class.my_method()

        # We know an exception was raised but we don't know how many 
        # times the method was called or if it even was called. All we 
        # know is that it should have been called between 1 and 3 times.
        (1, 3) * spock_mock_object.some_method.any()
        
        # Finally, we can check that the exception message is not modified.
        self.assertIn('Failure', str(context.exception))

```

## Practical Examples
Lets say you have a user service that talks with a database and you want to mock the database methods.
The databse object has a method `insert(name)` that returns an auto-incrementing id and the name of the user.
It also has a method called `get(id)` that retrieves the user for the provided ID and should raise an exception otherwise.

The user service should implement:
- `create_user(name)`, which adds a user to the database
- `get_user(id)`, which retrieves a user from the database for the provided ID
- `batch_get_users(ids)`, which retrieves all the users for the provided IDs

A simple test for something like this could be:
```python
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

        1 * self.mock_db.get.specific(-1)

    def test_batch_get_retrieves_users_from_the_database(self):
        first_user_id, first_name = self.user_service.create_user('user1')
        second_user_id, second_name = self.user_service.create_user('user2')

        found_users = self.user_service.batch_get_users([first_user_id, second_user_id])

        2 * self.mock_db.get.any()

        self.assertEqual(found_users[0], (first_user_id, first_name))
        self.assertEqual(found_users[1], (second_user_id, second_name))

    def test_batch_get_raises_exception_if_user_not_found(self):
        first_user_id, first_name = self.user_service.create_user('user1')
        second_user_id, second_name = self.user_service.create_user('user2')

        with self.assertRaises(Exception) as context:
            self.user_service.batch_get_users([first_user_id, second_user_id, -1])
        self.assertIn('Not found', str(context.exception))

        # Depending on the order we retrieve the items in, there should be between 1 and 3 calls
        (1, 3) * self.mock_db.get.any()

    def test_create_user_fails_if_db_is_down(self):
        def mock_db_failure(*_):
            raise Exception('DB failure')
        self.mock_db.insert.specific_mock_return(mock_db_failure, "' SELECT -- bad sql injection")

        with self.assertRaises(Exception) as context:
            self.user_service.create_user("' SELECT -- bad sql injection")
        self.assertIn('DB failure', str(context.exception))

        self.user_service.create_user("Valid user name")

    def test_create_user_has_default_user_name(self):
        self.user_service.create_user()
        1 * self.mock_db.insert.specific('Some name')

```
You can see this example in action in the `example/` folder
## Known issues
- There could be potential issues if using this as well as side_effects. This will probably be improved upon in the future.

## Features I would like to add
- Wildcards in the specific method call assertion.
Something like `1 * mocked_object.some_method.specific(ANY, 2)`, which would ignore the first argument and only match the second argument.
- Removing of old/unused specific mocks