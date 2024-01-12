from pytest import fixture
import socketio


# @pytest.fixture(autouse=True)
# def slow_down_tests():
#     yield
#     time.sleep(5)

@fixture(scope="module")
def sio():
    """Сокет уже получивший первое приветствие"""
    socket_object = socketio.SimpleClient()
    client = socket_object.connect('ws://0.0.0.0:80')
    # socket_object.receive()
    socket_object.emit('server/debug/reset_players', {})
    return socket_object


@fixture(scope="module")
def sio_2():
    """Сокет уже получивший первое приветствие"""
    socket_object = socketio.SimpleClient()
    client = socket_object.connect('ws://0.0.0.0:80')
    # socket_object.receive()
    return socket_object

