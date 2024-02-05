import pytest
from game_module.main import Pacman


@pytest.fixture
def pacman_instance():
    return Pacman(1, 1)  # You can adjust the initial position as needed


def test_pacman_initialization(pacman_instance):
    assert pacman_instance.row == 1
    assert pacman_instance.col == 1
    assert pacman_instance.mouthOpen is False


def test_pacman_update(pacman_instance):
    pacman_instance.newDir = 1
    pacman_instance.update()
    assert pacman_instance.dir == 1
    assert pacman_instance.col == 1.25  # Assuming the initial col is 1


def test_pacman_draw(pacman_instance):
    # Implement a mock version of screen.blit for testing
    def mock_blit(image, position):
        assert position == (1.0, 1.0, 32, 32)
    pacman_instance.draw(mock_blit)
