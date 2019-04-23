import unittest

from src import SpockMock


def mock_add_numbers(first_number, second_number):
    return first_number + second_number


class TestSpockMock(unittest.TestCase):

    def test_can_assert_number_of_mocked_calls(self):
        # Given: A mocked object
        spock_mock = SpockMock()

        # And: The mock object has a method for summing numbers
        spock_mock.add_numbers.mock_return = mock_add_numbers

        # When: That method is called
        ret = spock_mock.add_numbers(1, 2)

        # Then: The method is called once
        1 * spock_mock.add_numbers.any()

        # And: The correct value is returned
        self.assertEqual(ret, 3)

    def test_can_call_mock_with_named_argument(self):
        # Given: A mocked object
        spock_mock = SpockMock()

        # And: The mock object has a method for summing numbers
        spock_mock.add_numbers.mock_return = mock_add_numbers

        # When: That method is called
        ret = spock_mock.add_numbers(1, second_number=2)

        # Then: The method is called once
        1 * spock_mock.add_numbers.any()

        # And: The correct value is returned
        self.assertEqual(ret, 3)

    def test_can_call_mock_with_only_named_arguments(self):
        # Given: A mocked object
        spock_mock = SpockMock()

        # And: The mock object has a method for summing numbers
        spock_mock.add_numbers.mock_return = mock_add_numbers

        # When: That method is called
        ret = spock_mock.add_numbers(first_number=1, second_number=2)

        # Then: The method is called once
        1 * spock_mock.add_numbers.any()

        # And: The correct value is returned
        self.assertEqual(ret, 3)

    def test_mock_call_number_does_not_reset_after_checking(self):
        # Given: A mocked object
        spock_mock = SpockMock()

        # And: The mock object has a method for summing numbers
        spock_mock.add_numbers.mock_return = mock_add_numbers

        # When: That method is called
        ret = spock_mock.add_numbers(1, 2)

        # Then: The method is called once and returns the correct value
        1 * spock_mock.add_numbers.any()
        self.assertEqual(ret, 3)

        # When: The method is called again with different parameters
        ret = spock_mock.add_numbers(2, 3)

        # Then: The method is called twice
        2 * spock_mock.add_numbers.any()

        # And: The correct value is returned
        self.assertEqual(ret, 5)

    def test_can_assert_number_of_unmocked_calls(self):
        # Given: A mocked object
        spock_mock = SpockMock()

        # When: I make a call to an un-mocked method
        spock_mock.test_something_unmocked(1, 2)

        # Then: It is called once with any values
        1 * spock_mock.test_something_unmocked.any()

        # And: It is called once with values 1, 2
        1 * spock_mock.test_something_unmocked.specific(1, 2)

    def test_can_mock_call_with_uncallable_object(self):
        # Given: A mocked object
        spock_mock = SpockMock()

        # And: The object has a method called test_return_value that returns a constant
        spock_mock.test_return_value.mock_return = 5

        # When: A call is made to test_return_value
        ret = spock_mock.test_return_value()

        # Then: The method is called once
        1 * spock_mock.test_return_value.any()

        # And: The correct value is returned
        self.assertEqual(5, ret)

        # When: test_return_value is changed to return 6
        spock_mock.test_return_value.mock_return = 6

        # And: Another call is made to test_return_value
        ret = spock_mock.test_return_value()

        # Then: The method is called twice
        2 * spock_mock.test_return_value.any()

        # And: The correct value is returned
        self.assertEqual(6, ret)

    def test_can_assert_range_of_calls(self):
        # When: A mocked object is provided
        spock_mock = SpockMock()

        # Then: An exception is raised when checking if between 1 and 3 calls are made
        with self.assertRaises(AssertionError):
            (1, 3) * spock_mock.add_numbers.any()

        # When: A call is made to the same function
        spock_mock.add_numbers(1, 2)

        # Then: No exception is raised when checking if the number of calls is between 1 and 3
        (1, 3) * spock_mock.add_numbers.any()

        # When: A call is made to the same function
        spock_mock.add_numbers(1, 2)

        # Then: No exception is raised when checking if the number of calls is between 1 and 3
        (1, 3) * spock_mock.add_numbers.any()

        # When: A call is made to the same function
        spock_mock.add_numbers(1, 2)

        # Then: No exception is raised when checking if the number of calls is between 1 and 3
        (1, 3) * spock_mock.add_numbers.any()

        # When: A call is made to the same function
        spock_mock.add_numbers(1, 2)

        # Then: An exception is raised when checking if between 1 and 3 calls are made
        with self.assertRaises(AssertionError):
            (1, 3) * spock_mock.add_numbers.any()

    def test_can_assert_specific(self):
        # Given: A mocked object
        spock_mock = SpockMock()

        # When: A call is made to a method
        spock_mock.add_numbers()

        # Then: The method is called specifically once with no arguments
        1 * spock_mock.add_numbers.specific()

        # When: A call is made to the same method
        spock_mock.add_numbers(1, 2)

        # Then: The method is called specifically once with 1, 2
        1 * spock_mock.add_numbers.specific(1, 2)

        # When: A call is made to the same method with a named argument
        spock_mock.add_numbers(1, second_number=2)

        # Then: The method is called specifically once with 1, second_argument=2
        1 * spock_mock.add_numbers.specific(1, second_number=2)

        # When: A call is made to the same method with only named arguments
        spock_mock.add_numbers(first_number=1, second_number=2)

        # Then: The method is called specifically once with first_number=1, second_number=2
        1 * spock_mock.add_numbers.specific(first_number=1, second_number=2)

        # When: Multiple calls are made to the same method
        spock_mock.add_numbers()
        spock_mock.add_numbers(1, 2)
        spock_mock.add_numbers(1, second_number=2)
        spock_mock.add_numbers(first_number=1, second_number=2)

        # Then: There are 8 calls in total to the mocked method
        8 * spock_mock.add_numbers.any()

        # And: There are two calls for each argument call
        2 * spock_mock.add_numbers.specific()
        2 * spock_mock.add_numbers.specific(1, 2)
        2 * spock_mock.add_numbers.specific(1, second_number=2)
        2 * spock_mock.add_numbers.specific(first_number=1, second_number=2)

    def test_can_mock_specific(self):
        # Given: A mocked object
        spock_mock = SpockMock()

        # And: A function has a base mock
        spock_mock.add_numbers.mock_return = 1

        # And: A function with specific arguments is mocked
        spock_mock.add_numbers.specific_mock_return(3, 1, 2)

        # When: A call is made to the function with the specific arguments
        ret = spock_mock.add_numbers(1, 2)

        # Then: The method is called once
        1 * spock_mock.add_numbers.any()

        # And: The value returned is correct
        self.assertEqual(ret, 3)

        # When: Another call is made
        ret = spock_mock.add_numbers(1, 2)

        # Then: The method is called exactly twice with the same arguments
        2 * spock_mock.add_numbers.specific(1, 2)

        # And: The same value is returned
        self.assertEqual(ret, 3)

        # When: A call is made that is not specifically mocked
        ret = spock_mock.add_numbers(0, 1)

        # Then: The base mock value is returned
        self.assertEqual(1, ret)

        # And: The method is called 3 times
        3 * spock_mock.add_numbers.any()

        # And: The method is only called once for arguments 0, 1
        1 * spock_mock.add_numbers.specific(0, 1)

        # And: The method is only called twice for arguments 1, 2
        2 * spock_mock.add_numbers.specific(1, 2)
