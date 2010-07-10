"""
test_dispatch.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

Tests the Dispatch module.
"""
import unittest
from xbee.helpers.dispatch import Dispatch
from xbee.helpers.dispatch.tests.fake import FakeXBee

class CallbackCheck(object):
    def __init__(self):
        self.called = False
        
    def call(self, name, data):
        self.called = True

class TestDispatch(unittest.TestCase):
    """
    Tests xbee.helpers.dispatch for expected behavior
    """

    def setUp(self):
        self.xbee = FakeXBee(None)
        self.dispatch = Dispatch(xbee=self.xbee)
        self.callback_check = CallbackCheck()
        
    def test_callback_is_called_when_registered(self):
        """
        After registerring a callback function with a filter function,
        the callback should be called when data arrives.
        """
        self.dispatch.register("test1", self.callback_check.call, lambda data: True)
        self.dispatch.run(oneshot=True)
        self.assertTrue(self.callback_check.called)
        
    def test_callback_not_called_when_filter_not_satisfied(self):
        """
        After registerring a callback function with a filter function,
        the callback should not be called if a packet which does not
        satisfy the callback's filter arrives.
        """
        self.dispatch.register("test1", self.callback_check.call, lambda data: False)
        self.dispatch.run(oneshot=True)
        self.assertFalse(self.callback_check.called)
        
    def test_multiple_callbacks(self):
        """
        Many callbacks should be called on the same packet if each
        callback's filter method is satisfied.
        """
        callbacks = []
        
        for i in range(0,10):
            check = CallbackCheck()
            callbacks.append(check)
            self.dispatch.register("test%d" % i, check.call, lambda data: True)
            
        self.dispatch.run(oneshot=True)
        
        for callback in callbacks:
            if not callback.called:
                self.fail("All callback methods should be called")
        
