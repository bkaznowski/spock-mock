from unittest.mock import Mock


class SpockMock(Mock):
    # TODO find out how to implement the __init__, as it fails in unittest.Mock

    def __call__(self, *args, **kwargs):
        original_return_value = self.return_value
        mock_return = getattr(self, 'mock_return')
        if not isinstance(mock_return, SpockMock):
            self._handle_mock(args, kwargs, mock_return)

        specific_mocks = getattr(self, 'specific_mocks')
        if not isinstance(specific_mocks, SpockMock):
            for specific_mock in specific_mocks:
                specific_call, specific_args, specific_kwargs = specific_mock
                if specific_args == args and specific_kwargs == kwargs:
                    self._handle_mock(args, kwargs, specific_call)

        to_be_returned = super().__call__(*args, **kwargs)
        self.return_value = original_return_value
        return to_be_returned

    def _handle_mock(self, args, kwargs, mock_return):
        if callable(mock_return):
            if args and not kwargs:
                self.return_value = mock_return(*args)
            elif args and kwargs:
                self.return_value = mock_return(*args, **kwargs)
            elif not args and kwargs:
                self.return_value = mock_return(**kwargs)
            else:
                self.return_value = mock_return()
        else:
            self.return_value = mock_return

    def any(self):
        return AnySpockMock(self)

    def specific(self, *args, **kwargs):
        return SpecificSpockMock(self, args, kwargs)

    def mock_specific(self, return_call, *args, **kwargs):
        specific_mocks = getattr(self, 'specific_mocks')
        if isinstance(specific_mocks, SpockMock):
            specific_mocks = []
        specific_mocks.append((return_call, args, kwargs))
        self.specific_mocks = specific_mocks


class AnySpockMock:
    def __init__(self, mock):
        self.mock = mock

    def __rmul__(self, expected_call_count):
        if isinstance(expected_call_count, int):
            if expected_call_count != self.mock.call_count:
                raise AssertionError(
                    f'Expected {self.mock._mock_name} to be called '
                    f'{expected_call_count} times, but called {self.mock.call_count} times'
                )
        elif isinstance(expected_call_count, tuple) and len(expected_call_count) == 2:
            if self.mock.call_count < expected_call_count[0] or self.mock.call_count > expected_call_count[1]:
                raise AssertionError(
                    f'Expected {self.mock._mock_name} to be called '
                    f'between {expected_call_count[0]} and {expected_call_count[1]} times, but called '
                    f'{self.mock.call_count} times'
                )
        else:
            raise ValueError(f'Expected int or tuple but got {expected_call_count.__name__}')


class SpecificSpockMock:
    def __init__(self, mock, *args):
        self.mock = mock

        self.args, self.kwargs = args

    def __rmul__(self, expected_call_count):
        matched_calls_count = 0
        for args, kwagrs in self.mock.call_args_list:
            if args == self.args and kwagrs == self.kwargs:
                matched_calls_count += 1
        if isinstance(expected_call_count, int):
            if expected_call_count != matched_calls_count:
                raise AssertionError(
                    f'Expected {self.mock._mock_name} to be called '
                    f'{expected_call_count} times with {self.format_args(self.args, self.kwargs)}, '
                    f'but called {matched_calls_count} times {self.mock.call_args_list}'
                )
        elif isinstance(expected_call_count, tuple) and len(expected_call_count) == 2:
            if matched_calls_count < expected_call_count[0] or matched_calls_count > expected_call_count[1]:
                raise AssertionError(
                    f'Expected {self.mock._mock_name} to be called '
                    f'between {expected_call_count[0]} and {expected_call_count[1]} times '
                    f'with {self.format_args(self.args, self.kwargs)}, but called {matched_calls_count} times'
                )
        else:
            raise ValueError(f'Expected int or tuple but got {expected_call_count.__name__}')

    def format_args(self, args, kwargs):
        formatted = '('
        for arg in args:
            formatted = f'{formatted}{arg}, '
        for key_arg, value_arg in kwargs.items():
            formatted = f'{formatted}{key_arg}={value_arg}, '
        if len(formatted) > 1:
            formatted = formatted[:-2]
        formatted = f'{formatted})'
        return formatted
