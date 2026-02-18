import numpy as np
from merlin.utilities import trainola
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from merlin.utilities import get_joule_node


@pytest.mark.asyncio
async def test_get_joule_node():
    mock_node = MagicMock()
    mock_node.close = AsyncMock()

    with patch("joule.api.get_node", return_value=mock_node):
        async with get_joule_node("test-node") as node:
            assert node is mock_node

    mock_node.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_joule_node_exception():
    mock_node = MagicMock()
    mock_node.close = AsyncMock()

    with patch("joule.api.get_node", return_value=mock_node):
        with pytest.raises(RuntimeError):
            async with get_joule_node("test-node"):
                raise RuntimeError()

    mock_node.close.assert_awaited_once()


def test_trainola_same():
    a = np.ones((1, 30))
    a[:, :15] = 0
    assert np.isclose(trainola(a, a), 0)

    a = np.ones((24, 30))
    a[:, :15] = 0
    assert np.isclose(trainola(a, a), 0)


def test_trainola_uncorrelated():
    a = np.ones((1, 30))
    a[:, :15] = 0
    b = np.zeros((1, 30))
    assert np.isclose(trainola(a, b), 1)

    a = np.ones((24, 30))
    a[:, :15] = 0
    b = np.zeros((24, 30))
    assert np.isclose(trainola(a, b), 1)
