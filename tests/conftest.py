import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--docker-image",
        action="store",
        default=None,
        help="Docker image to use for testing. If not specified, all configured images will be tested.",
    )


@pytest.fixture
def docker_image(request):
    """Fixture that returns the docker image specified via command line or None."""
    docker_image = request.config.getoption("--docker-image")
    if docker_image is None:
        pytest.fail("Docker image not specified")
    return docker_image
