import os
import hashlib

from com.trimniu.util.FileOperatorUtil import FileUtil
from com.trimniu.util.LoggerUtil import Logger
from com.trimniu.util.ParamikoTools import SSHConnection
from com.trimniu.util.ServerInfo import ServerInfo


# 校验MD5值
def GetFileMd5(filename):
    if not os.path.isfile(filename):
        return
    myHash = hashlib.md5()
    f = open(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        myHash.update(b)
    f.close()
    return myHash.hexdigest()


if __name__ == '__main__':

    ssh = None

    try:

        log = Logger('all.log', level='debug')
        log.logger.debug('debug')
        # 初始化服务器信息
        index = 0
        remoteServerInfo = ServerInfo.getRemoteServerInfo(index=index)
        localServerInfo = ServerInfo.getLocalServerInfo(index=index)

        # 初始化ssh
        ssh = SSHConnection(host=remoteServerInfo.host, user=remoteServerInfo.user, port=remoteServerInfo.port,
                            privateKey=remoteServerInfo.pkeyPath)
        fileUtil = FileUtil(ssh=ssh)

        # 获取远程及本地文件列表
        fileUtil.gciRemote(remoteServerInfo.remotePath, remoteServerInfo.remoteDirNames,
                           remoteServerInfo.remoteFileNames)
        fileUtil.gciLocal(localServerInfo.localPath, localServerInfo.localDirNames, localServerInfo.localFileNames)

        fileUtil.getRemoteAllFileMd5(ssh, remoteServerInfo.remoteFileNames, remoteServerInfo.remotePath,remoteServerInfo.remoteFileMD5Dicts)

        print(str(remoteServerInfo.remoteFileMD5Dicts))

    finally:
        # 关闭ssh连接
        if ssh is not None:
            ssh.close()
