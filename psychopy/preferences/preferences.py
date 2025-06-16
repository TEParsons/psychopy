#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import json
import jsonschema
import os
import sys
import platform
from pathlib import Path
from psychopy import logging
from . import devices, parser
from .. import __version__

from packaging.version import Version
import shutil

join = os.path.join


class Preferences:
    """Users can alter preferences from the dialog box in the application,
    by editing their user preferences file (which is what the dialog box does)
    or, within a script, preferences can be controlled like this::

        import psychopy
        psychopy.prefs.hardware['audioLib'] = ['ptb', 'pyo','pygame']
        print(psychopy.prefs)
        # prints the location of the user prefs file and all the current vals

    Use the instance of `prefs`, as above, rather than the `Preferences` class
    directly if you want to affect the script that's running.
    """

    # Names of legacy parameters which are needed for use version
    legacy = [
        "winType",  # 2023.1.0
        "audioLib",  # 2023.1.0
        "audioLatencyMode",  # 2023.1.0
    ]

    def __init__(self):
        super(Preferences, self).__init__()
        self.userPrefsCfg = None  # the config object for the preferences
        self.prefsSpec = None  # specifications for the above
        # the config object for the app data (users don't need to see)
        self.appDataCfg = None

        self.general = None
        self.piloting = None
        self.coder = None
        self.builder = None
        self.connections = None
        self.paths = {}  # this will remain a dictionary
        self.keys = {}  # does not remain a dictionary

        # Only call loadAll, which will handle getPaths
        self.loadAll()
        # setting locale is now handled in psychopy.localization.init
        # as called upon import by the app

        if self.userPrefsCfg['app']['resetPrefs']:
            self.resetPrefs()

    def __str__(self):
        """pretty printing the current preferences"""
        strOut = "psychopy.prefs <%s>:\n" % (
            join(self.paths['userPrefsDir'], 'userPrefs.cfg'))
        for sectionName in ['general', 'coder', 'builder', 'connections']:
            section = getattr(self, sectionName)
            for key, val in list(section.items()):
                strOut += "  prefs.%s['%s'] = %s\n" % (
                    sectionName, key, repr(val))
        return strOut

    def resetPrefs(self):
        """removes userPrefs.cfg, does not touch appData.cfg
        """
        userCfg = join(self.paths['userPrefsDir'], 'userPrefs.cfg')
        try:
            os.unlink(userCfg)
        except Exception:
            msg = "Could not remove prefs file '%s'; (try doing it manually?)"
            print(msg % userCfg)
        self.loadAll()  # reloads, now getting all from .spec

    def getPaths(self, userDir=None):
        """Get the paths to various directories and files used by PsychoPy.

        If the paths are not found, they are created. Usually, this is only
        necessary on the first run of PsychoPy. However, if the user has
        deleted or moved the preferences directory, this method will recreate 
        those directories.

        """
        # on mac __file__ might be a local path, so make it the full path
        thisFileAbsPath = os.path.abspath(__file__)
        prefSpecDir = os.path.split(thisFileAbsPath)[0]
        dirPsychoPy = os.path.split(prefSpecDir)[0]
        exePath = sys.executable

        # path to Resources (icons etc)
        dirApp = join(dirPsychoPy, 'app')
        if os.path.isdir(join(dirApp, 'Resources')):
            dirResources = join(dirApp, 'Resources')
        else:
            dirResources = dirApp

        self.paths['psychopy'] = dirPsychoPy
        self.paths['appDir'] = dirApp
        self.paths['appFile'] = join(dirApp, 'PsychoPy.py')
        self.paths['demos'] = join(dirPsychoPy, 'demos')
        self.paths['resources'] = dirResources
        self.paths['assets'] = join(dirPsychoPy, "assets")
        self.paths['tests'] = join(dirPsychoPy, 'tests')
        self.paths['scripts'] = join(dirPsychoPy, 'scripts')
        # path to libs/frameworks
        if 'PsychoPy.app/Contents' in exePath:
            self.paths['libs'] = exePath.replace("MacOS/python", "Frameworks")
        else:
            self.paths['libs'] = ''  # we don't know where else to look!
        if not Path(self.paths['appDir']).is_dir():
            # if there isn't an app folder at all then this is a lib-only psychopy
            # so don't try to load app prefs etc
            NO_APP = True
        # get user dir
        if userDir is not None and os.path.isdir(userDir):
            self.paths['userPrefsDir'] = join(
                userDir, '.psychopy3'
            )
        elif sys.platform == 'win32':
            self.paths['userPrefsDir'] = join(
                os.environ['APPDATA'], 'psychopy3'
            )
        else:
            self.paths['userPrefsDir'] = join(
                os.environ['HOME'], '.psychopy3'
            )
        # get system-appropriate spec file
        if sys.platform == 'win32':
            self.paths['prefsSpecFile'] = join(prefSpecDir, 'Windows.spec')
        else:
            self.paths['prefsSpecFile'] = join(
                prefSpecDir, platform.system() + '.spec')
        # directory for files created by the app at runtime needed for operation
        self.paths['userCacheDir'] = join(self.paths['userPrefsDir'], 'cache')

        # paths in user directory to create/check write access
        userPrefsPaths = (
            'userPrefsDir',  # root dir
            'themes',  # define theme path
            'fonts',  # find / copy fonts
            'packages',  # packages and plugins
            'configs',  # config files for plugins
            'cache',  # cache for downloaded and other temporary files
        )

        # build directory structure inside user directory
        for userPrefPath in userPrefsPaths:
            # define path
            if userPrefPath != 'userPrefsDir':  # skip creating root, just check
                self.paths[userPrefPath] = join(
                    self.paths['userPrefsDir'],
                    userPrefPath)
            # avoid silent fail-to-launch-app if bad permissions:
            try:
                os.makedirs(self.paths[userPrefPath])
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise
        # make sure there's a device manager config file
        deviceCfgFile = self.paths['deviceCfgFile'] = Path(self.paths['userPrefsDir']) / "devices.json"
        if not deviceCfgFile.is_file():
            deviceCfgFile.write_text("{}", encoding="utf-8")
        # site-packages root directory for user-installed packages
        userPkgRoot = Path(self.paths['packages'])

        # Package paths for custom user site-packages, these should be compliant
        # with platform specific conventions.
        if sys.platform == 'win32':
            pyDirName = "Python" + sys.winver.replace(".", "")
            userPackages = userPkgRoot / pyDirName / "site-packages"
            userInclude = userPkgRoot / pyDirName / "Include"
            userScripts = userPkgRoot / pyDirName / "Scripts"
        elif sys.platform == 'darwin' and sys._framework:  # macos + framework
            pyVersion = sys.version_info
            pyDirName = "python{}.{}".format(pyVersion[0], pyVersion[1])

            # determine if we should use symlinks for the package folders if the
            # user already has package installed
            useSymlinks = (
                Path(self.paths['packages']) / 'include' / pyDirName).exists()

            # Standard scheme of lib directories for OSX framework does not
            # distinguish between python versions. We must modify the
            # site-packages root directory to provide a unique path for
            # each python version.
            userPkgRoot = Path(self.paths['packages']) / pyDirName
            try:
                os.makedirs(userPkgRoot)
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise
            
            if useSymlinks:
                # create symlinks to refer to the old package directories
                oldUserPackageRoot = Path(self.paths['packages'])
                userPackages = userPkgRoot / "lib"
                userInclude = userPkgRoot / "include"
                userScripts = userPkgRoot / "bin"

                # create symlinks to the python version agnostic directories
                if not userPackages.exists():
                    userPackages.symlink_to(oldUserPackageRoot / "lib")
                if not userInclude.exists():
                    userInclude.symlink_to(oldUserPackageRoot / "include")
                if not userScripts.exists():
                    userScripts.symlink_to(oldUserPackageRoot / "bin")

            # reload userPkgRoot
            self.paths['packages'] = userPkgRoot = Path(self.paths['packages'])  
            # See the ox_framework_user scheme standard:
            # https://docs.python.org/3/library/sysconfig.html#osx-framework-user
            userPackages = userPkgRoot / "lib" / "python" / "site-packages"
            userInclude = userPkgRoot / "include" / pyDirName
            userScripts = userPkgRoot / "bin"
        else:  # posix (including linux and macos without framework)
            pyVersion = sys.version_info
            pyDirName = "python{}.{}".format(pyVersion[0], pyVersion[1])
            userPackages = userPkgRoot / "lib" / pyDirName / "site-packages"
            userInclude = userPkgRoot / "include" / pyDirName
            userScripts = userPkgRoot / "bin"

        # populate directory structure for user-installed packages
        if not userPackages.is_dir():
            userPackages.mkdir(parents=True)
        if not userInclude.is_dir():
            userInclude.mkdir(parents=True)
        if not userScripts.is_dir():
            userScripts.mkdir(parents=True)

        # add paths from plugins/packages (installed by plugins manager)
        self.paths['userPackages'] = userPackages
        self.paths['userInclude'] = userInclude
        self.paths['userScripts'] = userScripts

        # Get dir for base and user themes
        baseThemeDir = Path(self.paths['appDir']) / "themes" / "spec"
        userThemeDir = Path(self.paths['themes'])
        # Check what version user themes were last updated in
        if (userThemeDir / "last.ver").is_file():
            with open(userThemeDir / "last.ver", "r") as f:
                lastVer = Version(f.read())
        else:
            # if no version available, assume it was the first version to have themes
            lastVer = Version("2020.2.0")
        # If version has changed since base themes last copied, they need updating
        updateThemes = lastVer < Version(__version__)
        # Copy base themes to user themes folder if missing or need update
        for file in baseThemeDir.glob("*.json"):
            if updateThemes or not (Path(self.paths['themes']) / file.name).is_file():
                shutil.copyfile(
                    file,
                    Path(self.paths['themes']) / file.name
                )

    def loadAll(self, userDir=None):
        """Load the user prefs and the application data
        """
        self.getPaths(userDir=userDir)

        # note: self.paths['userPrefsDir'] gets set in loadSitePrefs()
        self.paths['appDataFile'] = join(
            self.paths['userPrefsDir'], 'appData.cfg')
        self.paths['userPrefsFile'] = join(
            self.paths['userPrefsDir'], 'userPrefs.cfg')

        # If PsychoPy is tucked away by Py2exe in library.zip, the preferences
        # file cannot be found. This hack is an attempt to fix this.
        libzip = "\\library.zip\\psychopy\\preferences\\"
        if libzip in self.paths["prefsSpecFile"]:
            self.paths["prefsSpecFile"] = self.paths["prefsSpecFile"].replace(
                libzip, "\\resources\\")

        self.userPrefsCfg = self.loadUserPrefs()
        self.appDataCfg = self.loadAppData()

        # simplify namespace
        self.general = self.userPrefsCfg['general']
        self.app = self.userPrefsCfg['app']
        self.coder = self.userPrefsCfg['coder']
        self.builder = self.userPrefsCfg['builder']
        self.hardware = self.userPrefsCfg['hardware']
        self.piloting = self.userPrefsCfg['piloting']
        self.connections = self.userPrefsCfg['connections']
        self.appData = self.appDataCfg

        # keybindings:
        self.keys = self.userPrefsCfg['keyBindings']
    
    def loadFile(self, file, schemaFile):
        """
        Load preferences from a JSON file, supplying a JSON schema file to validate against and 
        derive defaults/fallbacks from.

        Parameters
        ----------
        file : pathlib.Path
            File to load prefs from
        schemaFile : pathlib.Path
            File to load schema from
        """
        # load schema from file
        with schemaFile.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        # try to load config
        try:
            with file.open("r", encoding="utf-8") as f:
                cfg = json.load(f)
        except FileNotFoundError as err:
            logging.debug(
                f"Failed find file {file}, reverting to defaults."
            )
            cfg = parser.defaults(schema)
        except json.decoder.JSONDecodeError as err:
            logging.error(
                f"Failed load file {file}, reverting to defaults. Reason: {err}"
            )
            cfg = parser.defaults(schema)
        # validate
        try:
            jsonschema.validate(cfg, schema=schema)
        except jsonschema.exceptions.ValidationError as err:
            # alert if validation fails
            logging.error(
                f"File {file} is invalid against schema {schemaFile}, attempting sanitization. Reason: {err}"
            )
            # try to sanitize
            try:
                parser.sanitize(cfg, schema=schema)
            except parser.JSONSanitizationError as err:
                logging.error(
                    f"Failed to sanitize app data file, reverting to defaults. Reason: {err}"
                )
                cfg = parser.defaults(schema)
        
        return cfg, schema
        

    def loadUserPrefs(self):
        """load user prefs, if any; don't save to a file because doing so
        will break easy_install. Saving to files within the psychopy/ is
        fine, eg for key-bindings, but outside it (where user prefs will
        live) is not allowed by easy_install (security risk)
        """
        # check/create path for user prefs
        if not os.path.isdir(self.paths['userPrefsDir']):
            try:
                os.makedirs(self.paths['userPrefsDir'])
            except Exception:
                msg = ("Preferences.py failed to create folder %s. Settings"
                       " will be read-only")
                print(msg % self.paths['userPrefsDir'])
        # load configuration from file
        cfg, self.prefsSpec = self.loadFile(
            file=Path(self.paths['userPrefsDir']) / "userPrefs.schema.json",
            schemaFile=Path(__file__).parent / "preferences.schema.json"
        )
        
        return cfg
    
    @property
    def devices(self):
        if not hasattr(self, "_devices"):
            self._devices = devices.DeviceConfig(
            self.paths['deviceCfgFile']
        )
        
        return self._devices

    def saveUserPrefs(self):
        """Validate and save the various setting to the appropriate files
        (or discard, in some cases)
        """
        # make sure folder exists
        if not os.path.isdir(self.paths['userPrefsDir']):
            os.makedirs(self.paths['userPrefsDir'])
        # save config
        file = Path(self.paths['userPrefsDir']) / "userPrefs.json"
        with file.open("w", encoding="utf-8") as f:
            json.dump(self.userPrefsCfg, f, cls=parser.ConfigEncoder, indent=True)

    def loadAppData(self):
        """Fetch app data config (unless this is a lib-only installation)
        """
        appDir = Path(self.paths['appDir'])
        if not appDir.is_dir():  # if no app dir this may be just lib install
            return {}
        # get configuration from file
        cfg, schema = self.loadFile(
            file=Path(self.paths['userPrefsDir']) / "appData.json",
            schemaFile=Path(self.paths['appDir']) / "appData.schema.json",
        )
        
        return cfg

    def saveAppData(self):
        """Save the various setting to the appropriate files
        (or discard, in some cases)
        """
        # make sure folder exists
        if not os.path.isdir(self.paths['userPrefsDir']):
            os.makedirs(self.paths['userPrefsDir'])
        # save config
        appDataFile = Path(self.paths['userPrefsDir']) / "appData.json"
        with appDataFile.open("w", encoding="utf-8") as f:
            json.dump(self.appDataCfg, f, cls=parser.ConfigEncoder, indent=True)


prefs = Preferences()
