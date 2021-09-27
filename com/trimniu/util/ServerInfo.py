# coding:utf-8

class RemoteServerInfo:

    # 创建RemoteServerInfo对象
    def __init__(self, host='xxx.xxx.xxx.xxx', port=22, user='xxx', pkeyPath='/xxx/xxx/id_rsa',
                 remotePath="/xxx/xxx/xxx/"):
        self.host = host
        self.port = port
        self.user = user
        self.pkeyPath = pkeyPath
        self.remotePath = remotePath
        self.remoteDirNames = []
        self.remoteFileNames = []
        self.remoteFileMD5Dicts = {}


class LocalServerInfo:

    # 创建LocalServerInfo对象
    def __init__(self, localPath="/xxx/xxx/xxx/"):
        self.localPath = localPath
        self.localDirNames = []
        self.localFileNames = []


class ServerInfo:

    @staticmethod
    def getRemoteServerInfo(index):
        remoteServerInfos = [];
        remoteServerInfos.append(
            RemoteServerInfo(host='192.168.3.7', port=22, user='admin', pkeyPath='/Users/trimniu/.ssh/id_rsa',
                             remotePath='/video/'))

        return remoteServerInfos[index]

    @staticmethod
    def getLocalServerInfo(index):
        localServerInfos = []
        localServerInfos.append(LocalServerInfo(localPath='/Users/trimniu/Downloads/video/'))

        return localServerInfos[index]
