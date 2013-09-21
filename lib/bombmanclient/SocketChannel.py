import socket
import struct

class SocketChannelFactory():
  '''
  Provides method to create channel connection.
  '''
  def openChannel(self, host, port):
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect((host, port))
      return SocketChannel(sock)
    except socket.error: 
      print "Cannot connect to {0} at port {1}. Please make sure the server is running.".format(host, port)
      raise
    
class SocketChannel():
  '''
  SocketChannel provides an abstraction layer above the 
  underlying socket, which sends and receives messages framed
  by their length as 4 bytes in Big Endian.
  '''
  def __init__(self, sock):
    self.sock = sock
    self.connected = True
  
  def write(self, byteStream):
    '''
    Write a byte stream message to the channel.
    The message will be prepended by its length packed
    in 4 bytes in Big Endian.
    '''
    streamLen = struct.pack('>L', len(byteStream))
    framedStream = streamLen + byteStream
    try:
      self.sock.sendall(framedStream)
    except socket.error:
      self.close()
      raise Exception("socket send fail, close")
      
  def read(self):
    '''
    Read a byte stream message prepended by its length
    in 4 bytes in Big Endian from channel.
    The message content is returned.
    '''
    lenField = self.readnbytes(4)
    length = struct.unpack('>L', lenField)[0]
    byteStream = self.readnbytes(length)
    return byteStream
  
  def readnbytes(self, n):
    buf = ''
    while n > 0:
      data = self.sock.recv(n)
      if data == '':
        raise Exception("socket broken or connection closed")
      buf += data
      n -= len(data)
    return buf

  def close(self):
    print("closing connection")
    self.sock.close()
    self.connected = False
    
    