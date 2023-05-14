from pathlib import Path
import shutil
import joblib
from meetup.logging import logInfo
from networkx import MultiDiGraph
import geopandas as gp

GeoCacheFormat = "flatgeobuff"


class Cache:
    def __init__(self, location: str = "./.data_cache"):
        self.baseDir = Path(location)
        self.runName = None

        if not self.baseDir.exists():
            logInfo(f"Generating cache folder at [bold white]{location}[/bold white]")
            self.baseDir.mkdir()

    def _run_dir(self):
        if self.runName is None:
            raise Exception("Must set a run name before using cache")
        return self.baseDir / self.runName

    def set_run_name(self, runName: str):
        self.runName = runName
        self.runDir = self.baseDir / runName
        if not self.runDir.exists():
            logInfo(f"Generating run folder at [bold white]{self.runDir}[/bold white]")
            self.runDir.mkdir()

    def clear_cache(self):
        shutil.rmtree(self._run_dir())

    def clear_cache_all(self):
        shutil.rmtree(self.baseDir)

    def get_cached_geo_data_frame(self, file: str) -> gp.GeoDataFrame | None:
        filePath = self._run_dir() / file
        if filePath.exists() and filePath.is_file():
            return joblib.load(filePath)
        else:
            return None

    def cache_geo_data_frame(self, file: str, df: gp.GeoDataFrame):
        filePath = self._run_dir() / file
        if filePath.exists():
            filePath.unlink()
        joblib.dump(df, filePath)

    def get_network(self, file: str) -> MultiDiGraph | None:
        filePath = self._run_dir() / file
        if filePath.exists() and filePath.is_file():
            return joblib.load(filePath)
        else:
            return None

    def set_network(self, file: str, network: MultiDiGraph):
        filePath = self._run_dir() / file
        if filePath.exists():
            filePath.unlink()
        joblib.dump(network, filePath)


RunCache = Cache()
