from shooter.osc.config import PORT
from shooter.osc.server import OscServer
from shooter.osc.dj import Dj

def test_osc_connect():
    server = OscServer(PORT)

