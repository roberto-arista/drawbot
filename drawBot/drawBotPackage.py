import os
import shutil
import plistlib
from packaging import version
import tempfile
from dataclasses import dataclass

from drawBot.drawBotSettings import __version__
from drawBot.scriptTools import ScriptRunner
from drawBot.drawBotDrawingTools import _drawBotDrawingTool

"""
DrawBot support for .drawbot packages.

* Read and build packages.
* Run packages

    MyTool.drawbot (package)
        info.plist
        lib/
            main.py
            anotherScript.py
            anImage.jpg

    info.plist
        name: optional, default to <name>.drawBot
        version: optional, default to 0.0, but advised to set
        developer: optional, default to None
        developerURL: optional, default to None
        requiresVersion: optional, default to all versions
        mainScript: optional, default to 'lib/main.py' if this isn't specified?)

"""

drawBotVersion = version.Version(__version__)


@dataclass
class DrawBotPackageInfo:
    name: str = ""
    version: str = "0.0"
    developer: str = ""
    developerURL: str = ""
    requiresVersion: str = "0.0"
    mainScript: str = "main.py"

    def validate(self):
        for key, value in self.__annotations__.items():
            assert isinstance(getattr(self, key), value)

    def asDict(self):
        """
        Return only keys which are different from the defaults.
        """
        defaults = dict(self.__class__().__dataclass_fields__)
        data = self.__dataclass_fields__
        for key, value in defaults.items():
            if data[key] == value:
                del data[key]
        return data

    def fromDict(self, data):
        """
        Set data from dict.
        """
        for key, value in data.items():
            setattr(self, key, value)


class DrawBotPackage:
    def __init__(self, path=None):
        self.path = path
        self.info = DrawBotPackageInfo()
        self._readInfo()

    def _readInfo(self):
        """
        Read the info.plist if the file is availble.
        """
        # get the info.plist path
        infoPath = self.infoPath()
        if infoPath and os.path.exists(infoPath):
            with open(infoPath, "rb") as f:
                info = plistlib.load(f)
            self.info.fromDict(info)
            # validate incoming info
            self.info.validate()

    def infoPath(self):
        """
        Return the info.plist path.
        Return None if there is no root path.
        """
        if self.path:
            return os.path.join(self.path, "info.plist")
        return None

    def mainScriptPath(self):
        """
        Return the main scripting python file path.
        Return None if ther is no root path.
        """
        if self.path:
            return os.path.join(self.path, "lib", self.info.mainScript)
        return None

    def run(self):
        """
        Execute the .drawBot package.
        Return if executing was succesfull with a report on failure.
        """
        # check if the package can run in this version of DrawBot
        if version.Version(self.info.requiresVersion) > drawBotVersion:
            return False, "Requires a newer version of DrawBot (%s)." % self.info.requiresVersion
        # get the main scriptin path
        path = self.mainScriptPath()
        if path is None:
            return False, "Cannot execute an empty package."
        if not os.path.exists(path):
            return False, "Cannot find '%s'." % path
        # create a namespace
        namespace = {}
        # add the tool callbacks in the name space
        _drawBotDrawingTool._addToNamespace(namespace)
        # run the script
        ScriptRunner(path=path, namespace=namespace)
        return True, ""

    def buildPackage(self, destinationPath, scriptRoot):
        """
        Build a .drawbot package
        """
        if not destinationPath.endswith(".drawbot"):
            return False, "The path to save the package must have a .drawbot file extension."
        # check if the script root exists
        if not os.path.exists(scriptRoot):
            return False, "Cannot find the script root '%s'" % scriptRoot
        # check if the main script path exists
        mainScriptPath = os.path.join(scriptRoot, self.info.mainScript)
        if not os.path.exists(mainScriptPath):
            return False, "Main script path '%s' does not exists in '%s'." % (self.info.mainScript, mainScriptPath)
        # build packages in temp folder
        tempDir = tempfile.mkdtemp()
        # set the temp folder
        self.path = tempDir
        # validate info
        self.info.validate()
        # write the plist
        infoData = self.info.asDict()
        # only write info that is different from
        if infoData:
            with open(self.infoPath(), "wb") as f:
                plistlib.dump(infoData, f)
        # build lib root path
        libRoot = os.path.join(self.path, "lib")
        # copy the script root
        shutil.copytree(scriptRoot, libRoot)
        # remove existing destination paths
        if os.path.exists(destinationPath):
            shutil.rmtree(destinationPath)
        # copy the temp to the destination path
        shutil.copytree(tempDir, destinationPath)
        # remove the temp
        shutil.rmtree(tempDir)
        # set the destination path
        self.path = destinationPath
        return True, ""


# ####

# # an empty package
# p = DrawBotPackage()
# print(p.path)
# print(p.info.name)
# print(p.infoPath())
# print(p.info)

# # create on the deskop such a file
# tempScriptDir = tempfile.mkdtemp()
# with open(os.path.join(tempScriptDir, "main.py"), "w") as f:
#     f.write("print('hello world! Im running from a .drawbot package!!')")

# packagePath = os.path.expanduser(os.path.join("~", "Desktop", "simple.drawbot"))
# package = DrawBotPackage()
# package.buildPackage(packagePath, tempScriptDir)
# shutil.rmtree(tempScriptDir)

# p = DrawBotPackage(packagePath)
# print(p.path)
# print(p.info.name)
# print(p.infoPath())
# print(p.info)
# print(p.run())
