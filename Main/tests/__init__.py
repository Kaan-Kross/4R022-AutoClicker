import os
import tempfile

# Isolate all tests from the real user profile.
os.environ.setdefault("AUTOCLICKER_4R022_HOME", tempfile.mkdtemp(prefix="4r022-test-"))
