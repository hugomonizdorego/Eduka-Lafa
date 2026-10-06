"""Same-user activation with framed, bounded messages and connection expiry."""
import hashlib
from .qt import QObject,Signal,QTimer,QLocalServer,QLocalSocket

MODES={'desktop','settings','configure','virtual','enable','disable','reload'}
def server_name(config_directory):
    return 'lafa-'+hashlib.sha256(str(config_directory.resolve()).encode()).hexdigest()[:20]

def activate_existing(name,mode='desktop'):
    if mode not in MODES:raise ValueError('Unknown LAFA launch role.')
    socket=QLocalSocket();socket.connectToServer(name)
    if not socket.waitForConnected(1500):return False
    socket.write((mode+'\n').encode('ascii'));socket.flush()
    if socket.bytesToWrite() and not socket.waitForBytesWritten(1000):socket.abort();return False
    socket.disconnectFromServer();return True

class ActivationServer(QObject):
    activated=Signal(str)
    def __init__(self,name,parent=None):
        super().__init__(parent);self.name=name;self.sockets={};self.server=QLocalServer(self)
        self.server.setSocketOptions(QLocalServer.UserAccessOption)
        QLocalServer.removeServer(name) # The caller must already hold the instance lock.
        if not self.server.listen(name):raise RuntimeError(self.server.errorString())
        self.server.newConnection.connect(self.accept)
    def accept(self):
        while self.server.hasPendingConnections():
            socket=self.server.nextPendingConnection();socket.setReadBufferSize(33)
            if len(self.sockets)>=16:socket.abort();socket.deleteLater();continue
            self.sockets[socket]=bytearray()
            timer=QTimer(socket);timer.setSingleShot(True);timer.timeout.connect(socket.abort);timer.start(2000)
            socket.readyRead.connect(lambda s=socket:self.receive(s));socket.disconnected.connect(lambda s=socket:self.cleanup(s))
            if socket.bytesAvailable():self.receive(socket)
    def receive(self,socket):
        if socket not in self.sockets:return
        message=self.sockets[socket];message.extend(bytes(socket.readAll()))
        if len(message)>32:socket.abort();return
        if b'\n' not in message:return
        try:mode=bytes(message).decode('ascii').removesuffix('\n')
        except UnicodeError:mode=''
        if mode in MODES:self.activated.emit(mode)
        socket.disconnectFromServer()
    def cleanup(self,socket):self.sockets.pop(socket,None);socket.deleteLater()
    def close(self):
        self.server.close()
        for socket in list(self.sockets):socket.abort()
