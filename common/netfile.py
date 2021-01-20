import clr
from System.IO import FileStream, FileMode
from System import String


class NetFile:
    def __init__(self, filename, mode):
        self.filename = filename
        if mode == 'w':
            self.mode = FileMode.Truncate
        else:
            self.mode = FileMode.Open
        self.file_stream = FileStream.Overloads[String, FileMode](filename, self.mode)

    def read(self):
        arr = []
        while True:
            b = self.file_stream.ReadByte()
            if b == -1: break
            else: arr.append(b)
        return bytes(arr).decode('utf-8')

    def write(self, string):
        b = string.encode('utf-8')
        self.file_stream.Write(b, 0, len(b))
        pass

    def close(self):
        self.file_stream.Finalize()

    def __del__(self):
        self.close()

if __name__ == '__main__':
    nfo = NetFile(r'D:\OneDrive\WorkBox\Python\SeleniumProject\JSON\out.txt', 'w')
    nfo.write('hello!')
    nfo.close()
    nfo_2 = NetFile(r'D:\OneDrive\WorkBox\Python\SeleniumProject\JSON\out.txt', 'r')
    print(nfo_2.read())
