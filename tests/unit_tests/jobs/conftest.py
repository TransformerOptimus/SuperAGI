# content of conftest.py
def pytest_configure(config):
    import sys
    sys._called_from_test = True

def pytest_unconfigure(config):
    import sys  # This was missing from the manual
    del sys._called_from_test
