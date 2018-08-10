import serial as ser
import GenericEvent as GE
import atgmPacket as AP

class SerialMedia(object):
    """
    Class description
    """
    # constructor
    def __init__(self, unix_path_to_port, baudrate):
        self.port = unix_path_to_port
        self.baudrate = baudrate
        self._media = ser.Serial(self.port, self.baudrate)
        self.responseEventSig = {'data':None}
        self.responseEvent = GE.GenericEvent(self.responseEventSig)

    def send(self, data, response_tally):
        """
        @params:
            data - is a sequence of bytes
            response_tally - how many bytes is it expecting in response
        @return:
            number of bytes written
        """
        number_of_bytes_sent = self._media.write(data)
        response = self._media.read(response_tally)
        self._parse(response)
        return number_of_bytes_sent

    def _parse(self, data):
        """
        @params:
            data - data recieved from remote serial port
        @return:
            None
        """
        if chr(data[0]) == '$' and chr(data[-1] == ';'):
            if self.responseEvent.isSubscribed:
                self.responseEvent(data=data[1:-1])

    # boolean property to check if the port is open
    @property
    def is_open(self):
        """
        returns the state of the serial media port, whether open or not
        """
        return self._media.is_open
    # release resources
    def release(self):
        self._media.close()

