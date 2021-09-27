# coding:utf-8

from com.trimniu.util.FileOperatorUtil import FileUtil
from com.trimniu.util.ServerInfo import ServerInfo
from com.trimniu.util.ParamikoTools import SSHConnection

if __name__ == '__main__':

    ssh = None

    try:

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

        # remote->local dir syn
        fileUtil.synDirFromRemoteToLocal(remotePath=remoteServerInfo.remotePath, localPath=localServerInfo.localPath,
                                         remoteDirNames=remoteServerInfo.remoteDirNames)
        # local->remote dir syn
        fileUtil.synDirFromLocalToRemote(localPath=localServerInfo.localPath, remotePath=remoteServerInfo.remotePath,
                                         localDirNames=localServerInfo.localDirNames)
        # local->remote file syn
        fileUtil.synFileFromLocalToRemote(localPath=localServerInfo.localPath, remotePath=remoteServerInfo.remotePath,
                                          localFileNames=localServerInfo.localFileNames)
        # remote->local file syn
        fileUtil.synFileFromRemoteToLocal(remotePath=remoteServerInfo.remotePath, localPath=localServerInfo.localPath,
                                          remoteFileNames=remoteServerInfo.remoteFileNames)

    finally:
        # 关闭ssh连接
        if ssh is not None:
            ssh.close()
