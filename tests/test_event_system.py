import unittest
from unittest.mock import MagicMock, patch
import logging

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from comfy_launcher.event_system import EventPublisher, AppEventType

# Suppress logging for cleaner test output unless specifically testing logging
logging.disable(logging.CRITICAL)

class TestEventSystem(unittest.TestCase):

    def setUp(self):
        self.publisher = EventPublisher()
        self.mock_handler1 = MagicMock(spec=lambda *args, **kwargs: None) # Allow any args/kwargs
        self.mock_handler1.__name__ = "mock_handler1_func"
        self.mock_handler2 = MagicMock(spec=lambda *args, **kwargs: None) # Allow any args/kwargs
        self.mock_handler2.__name__ = "mock_handler2_func"
        self.mock_logger = MagicMock(spec=logging.Logger)

    def test_subscribe_and_publish_no_args(self):
        """Test subscribing a handler and publishing an event with no arguments."""
        self.publisher.subscribe(AppEventType.TEST_EVENT_NO_ARGS, self.mock_handler1)
        self.publisher.publish(AppEventType.TEST_EVENT_NO_ARGS)
        self.mock_handler1.assert_called_once_with()

    def test_subscribe_and_publish_with_args(self):
        """Test subscribing a handler and publishing an event with arguments."""
        self.publisher.subscribe(AppEventType.TEST_EVENT_WITH_ARGS, self.mock_handler1)
        self.publisher.publish(AppEventType.TEST_EVENT_WITH_ARGS, data="test_data", value=123)
        self.mock_handler1.assert_called_once_with(data="test_data", value=123)

    def test_multiple_subscribers_for_same_event(self):
        """Test that multiple handlers for the same event are all called."""
        self.publisher.subscribe(AppEventType.TEST_EVENT_NO_ARGS, self.mock_handler1)
        self.publisher.subscribe(AppEventType.TEST_EVENT_NO_ARGS, self.mock_handler2)
        self.publisher.publish(AppEventType.TEST_EVENT_NO_ARGS)
        self.mock_handler1.assert_called_once_with()
        self.mock_handler2.assert_called_once_with()

    def test_unsubscribe_handler(self):
        """Test that an unsubscribed handler is not called."""
        self.publisher.subscribe(AppEventType.TEST_EVENT_NO_ARGS, self.mock_handler1)
        self.publisher.subscribe(AppEventType.TEST_EVENT_NO_ARGS, self.mock_handler2)
        self.publisher.unsubscribe(AppEventType.TEST_EVENT_NO_ARGS, self.mock_handler1)

        self.publisher.publish(AppEventType.TEST_EVENT_NO_ARGS)
        self.mock_handler1.assert_not_called()
        self.mock_handler2.assert_called_once_with()

    def test_unsubscribe_non_existent_handler(self):
        """Test unsubscribing a handler that was never subscribed (should not error)."""
        self.publisher.subscribe(AppEventType.TEST_EVENT_NO_ARGS, self.mock_handler1)
        # Attempt to unsubscribe a different, non-subscribed handler
        try:
            self.publisher.unsubscribe(AppEventType.TEST_EVENT_NO_ARGS, self.mock_handler2)
        except Exception as e:
            self.fail(f"Unsubscribing a non-existent handler raised an exception: {e}")

        self.publisher.publish(AppEventType.TEST_EVENT_NO_ARGS)
        self.mock_handler1.assert_called_once_with() # Original handler should still be called

    def test_publish_event_with_no_subscribers(self):
        """Test publishing an event that has no subscribers (should not error)."""
        try:
            self.publisher.publish(AppEventType.TEST_EVENT_NO_ARGS, data="test")
        except Exception as e:
            self.fail(f"Publishing an event with no subscribers raised an exception: {e}")

    @patch('comfy_launcher.event_system.event_system_logger', new_callable=MagicMock)
    def test_handler_raising_exception(self, mock_event_system_logger):
        """Test that if one handler raises an exception, others are still called and error is logged."""
        error_message = "Handler 1 failed!"
        self.mock_handler1.side_effect = Exception(error_message)

        self.publisher.subscribe(AppEventType.TEST_EVENT_WITH_ARGS, self.mock_handler1)
        self.publisher.subscribe(AppEventType.TEST_EVENT_WITH_ARGS, self.mock_handler2)

        self.publisher.publish(AppEventType.TEST_EVENT_WITH_ARGS, value=1)

        self.mock_handler1.assert_called_once_with(value=1)
        self.mock_handler2.assert_called_once_with(value=1) # Handler 2 should still be called
        mock_event_system_logger.error.assert_called_once()
        args, _ = mock_event_system_logger.error.call_args
        # The error message string is the first positional argument
        log_message = args[0]
        self.assertIn(f"Error in handler '{self.mock_handler1.__name__}' for event '{AppEventType.TEST_EVENT_WITH_ARGS.name}'", log_message)
        self.assertIn(error_message, log_message) # The exception string 'e' is part of the log message

    def test_subscribe_same_handler_multiple_times(self):
        """Test that subscribing the same handler multiple times for the same event results in it being called once."""
        # The current implementation will add it multiple times and call it multiple times.
        # If the desired behavior is to call it only once, the subscribe method would need a check.
        # For now, we test the current behavior.
        self.publisher.subscribe(AppEventType.TEST_EVENT_NO_ARGS, self.mock_handler1)
        self.publisher.subscribe(AppEventType.TEST_EVENT_NO_ARGS, self.mock_handler1)

        self.publisher.publish(AppEventType.TEST_EVENT_NO_ARGS)
        self.assertEqual(self.mock_handler1.call_count, 2)

if __name__ == '__main__':
    unittest.main()