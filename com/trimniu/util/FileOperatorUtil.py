# coding:utf-8
import os
import time
import datetime
import importlib, sys
import hashlib
from com.trimniu.util.LoggerUtil import Logger


class FileUtil:

    # 创建RemoteServerInfo对象
    def __init__(self, ssh):
        self.ssh = ssh
        self.fileUploadStartTime = datetime.datetime.now()
        self.preffix = "     "
        self.log = Logger('/Users/trimniu/Downloads/log/filmUp.log', level='debug')
        self.action = ''
        # self.download_file_key_word = "学打羽毛球"
        self.download_file_key_word = "星球大战"

    # 递归遍历远程目录下的所有文件
    def gciRemote(self, remote_path, remoteDirNames, remoteFileNames):
        for remoteFile in self.ssh.listdirattr(remote_path):
            if (str(remoteFile.longname).split(" ")[0].startswith('d')):
                remoteDirNames.append(os.path.join(remote_path, remoteFile.filename + "/"))
                self.gciRemote(os.path.join(remote_path, remoteFile.filename + "/"), remoteDirNames, remoteFileNames)
            else:
                remoteFileNames.append(os.path.join(remote_path, remoteFile.filename))

        return remoteDirNames

    # 获取本地制定目录下所有文件及目录名
    def gciLocal(self, file_dir, localDirNames, localFileNames):
        for root, dirs, files in os.walk(file_dir):
            localDirNames.append(root)  # 当前目录路径

            for file in files:
                if (file.__eq__(".DS_Store")):  # 忽略mac下 .DS_Store 隐藏文件
                    continue

                if (file.endswith("/")):
                    localFileNames.append(root + file)  # 当前路径下所有非目录子文件
                else:
                    localFileNames.append(root + "/" + file)  # 当前路径下所有非目录子文件

    # 打印进度信息
    def progress_bar(self, transferred, toBeTransferred, suffix=''):
        # 打印bar
        bar_len = 100
        filled_len = int(round(bar_len * transferred / float(toBeTransferred)))
        percents = round(100.0 * transferred / float(toBeTransferred), 1)
        bar = '\033[32;1m%s\033[0m' % '=' * filled_len + '-' * (bar_len - filled_len)

        # 计算花费时间、上传速度以及剩余时间
        microseconds = (datetime.datetime.now() - self.fileUploadStartTime).microseconds + (
                datetime.datetime.now() - self.fileUploadStartTime).seconds * 1000 * 1000
        totalSeconds = round(microseconds / (1000 * 1000), 4)
        speed = round(1.0 * transferred / (1024 * 1024 * totalSeconds), 1)
        ETA = time.strftime("%M:%S", time.localtime(round(((toBeTransferred - transferred) / (1024 * 1024)) / speed)))
        ST = time.strftime("%M:%S", time.localtime(totalSeconds))

        progressInfo = '[%s] %s%s %s%s %s%s %s %s %s %s %s\r' % (
            bar, '\033[32;1m%s\033[0m' % percents, '%', '\033[32;1m%s\033[0m' % round(transferred / (1024 * 1024)), 'M',
            '\033[32;1m%s\033[0m' % speed, 'M/S', '\033[32;1m%s\033[0m' % ETA, 'ETA', '\033[32;1m%s\033[0m' % ST, 'ST',
            suffix);

        if (transferred == toBeTransferred):
            self.log.logger.info(self.preffix + '结束' + self.action + '：' + progressInfo)
        else:
            sys.stdout.write(self.preffix + progressInfo)
            sys.stdout.flush()

    # remote->local dir syn
    def synDirFromRemoteToLocal(self, remotePath, localPath, remoteDirNames):
        self.log.logger.info("开始从远程目录：" + remotePath + " 向本地目录：" + localPath + " 同步文件夹")
        for remoteDir in remoteDirNames:
            newFilePath = remoteDir.replace(remotePath, localPath)
            if not os.path.exists(newFilePath):
                self.log.logger.info(self.preffix + "创建本地目录：" + newFilePath)
                os.mkdir(newFilePath)

    # local->remote dir syn
    def synDirFromLocalToRemote(self, localPath, remotePath, localDirNames):
        self.log.logger.info("开始从本地目录：" + localPath + " 向远程目录：" + remotePath + " 同步文件夹")
        for localDir in localDirNames:
            waitCreateRemoteDir = localDir.replace(localPath, remotePath)
            if (not self.ssh.isExists(waitCreateRemoteDir)):
                self.log.logger.info(self.preffix + "创建远程目录：" + waitCreateRemoteDir)
                self.ssh.mkdir(waitCreateRemoteDir)

    # local->remote file syn
    def synFileFromLocalToRemote(self, localPath, remotePath, localFileNames):
        self.log.logger.info("开始从本地目录：" + localPath + " 向远程目录：" + remotePath + " 同步文件")
        for localFile in localFileNames:
            waitUploadFile = localFile.replace(localPath, remotePath)

            # 如果文件不存在
            if not self.ssh.isExists(waitUploadFile):
                self.upload(localFile, waitUploadFile)

            # 如果文件存在，比对大小
            else:
                waitUploadFileSize = self.ssh.sftp.stat(waitUploadFile).st_size
                localFileSize = os.path.getsize(localFile)
                if (localFileSize > waitUploadFileSize):
                    self.upload(localFile, waitUploadFile)
                else:
                    self.log.logger.info(self.preffix + waitUploadFile + "文件已存在，无需上传")

    # remote->local syn
    def synFileFromRemoteToLocal(self, remotePath, localPath, remoteFileNames):
        self.log.logger.info("开始从远程目录：" + remotePath + " 向本地目录：" + localPath + " 同步文件")
        for remoteFile in remoteFileNames:

            if self.download_file_key_word not in remoteFile:
                continue

            localDownloadFile = remoteFile.replace(remotePath, localPath)
            # 如果文件不存在
            if os.path.exists(localDownloadFile):
                waitDownloadFileSize = os.path.getsize(localDownloadFile)
                remoteFileSize = self.ssh.sftp.stat(remoteFile).st_size
                if (waitDownloadFileSize != remoteFileSize):
                    self.download(remoteFile, localDownloadFile)
                else:
                    self.log.logger.info(self.preffix + localDownloadFile + "文件已存在，无需下载")
            else:
                self.download(remoteFile, localDownloadFile)

    # 从local向remote上传文件
    def upload(self, localFile, waitUploadFile):
        self.action = '上传'
        self.fileUploadStartTime = datetime.datetime.now()
        self.log.logger.info(self.preffix + "开始" + self.action + "：" + waitUploadFile)
        self.ssh.upload(localFile, waitUploadFile, self.progress_bar)
        self.action = ''

    # 从remote向local下载文件
    def download(self, remoteFile, localDownloadFile):
        self.action = '下载'
        self.fileUploadStartTime = datetime.datetime.now()
        self.log.logger.info(self.preffix + "开始" + self.action + "：" + localDownloadFile)
        self.ssh.download(localDownloadFile, remoteFile, self.progress_bar)
        self.action = ''

    # 获取本地文件校验MD5值
    def GetLocalFileMd5(self, filename):
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

    # 获取远程文件校验MD5值
    def GetRemoteFileMd5(self, ssh, filename):
        readout = ssh.cmd('md5sum ' + filename.replace('/video','/volume1/video') + '| cut -d" " -f1')

        print('md5sum ' + filename.replace('/video','/volume1/video') + '| cut -d" " -f1')
        md5 = str(readout).replace("b'", '')
        md5 = md5.replace("\\n'", '')
        return md5

    # 计算远程文件所有的Md5值
    def getRemoteAllFileMd5(self, ssh, remoteFileNames, remotePath, remoteFileMD5Dicts):
        self.log.logger.info("开始计算远程目录：" + remotePath + " 下所文件的MD5值")
        for remoteFile in remoteFileNames:
            fileMd5 = self.GetRemoteFileMd5(ssh, remoteFile)
            self.log.logger.info(self.preffix + remoteFile + " 文件md5值为：" + fileMd5)
            remoteFileMD5Dicts[fileMd5] = remoteFile