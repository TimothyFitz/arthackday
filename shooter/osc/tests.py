from config import PORT
from dj import Dj
from server import OscServer

def test_osc_connect():
    server = OscServer(PORT)

