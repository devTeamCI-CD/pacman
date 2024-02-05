import pytest
from game_module.main import Ghost


@pytest.fixture
def ghost_instance():
    return Ghost(1, 1, "red", 5)  # You can adjust the initial position and color as needed


def test_ghost_initialization(ghost_instance):
    assert ghost_instance.row == 1
    assert ghost_instance.col == 1
    assert ghost_instance.attacked is False


def test_ghost_update(ghost_instance):
    ghost_instance.setTarget()  # Assuming setTarget is working correctly
    initial_row, initial_col = ghost_instance.row, ghost_instance.col
    ghost_instance.update()
    assert ghost_instance.row != initial_row or ghost_instance.col != initial_col


def test_ghost_draw(ghost_instance):
    # Implement a mock version of screen.blit for testing
    def mock_blit(image, position):
        assert position == (1.0, 1.0, 32, 32)

    ghost_instance.draw(mock_blit)
