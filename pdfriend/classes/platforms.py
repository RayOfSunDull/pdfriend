import platformdirs
import pathlib
import shutil

def ensuredir(path: pathlib.Path):
    if not path.exists():
        path.mkdir()


class Platform:
    ConfigDir = platformdirs.user_config_path().joinpath("pdfriend")
    CacheDir = platformdirs.user_cache_path().joinpath("pdfriend")
    TempDir = CacheDir.joinpath("temp")

    @classmethod
    def Init(cls): # make sure the system directories exist
        ensuredir(cls.ConfigDir)
        ensuredir(cls.CacheDir)

        if cls.TempDir.exists(): # temp dir always cleared on startup
            shutil.rmtree(cls.TempDir.as_posix())
        cls.TempDir.mkdir()
    
    @classmethod
    def NewTemp(cls, path_name: str):
        return cls.TempDir.joinpath(path_name)