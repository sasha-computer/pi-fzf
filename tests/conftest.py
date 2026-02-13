from pathlib import Path

import pytest

TESTDATA = Path(__file__).parent.parent / "testdata"


@pytest.fixture
def testdata() -> Path:
    return TESTDATA
