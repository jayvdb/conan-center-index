import os

from textwrap import dedent

import yaml

from conans import ConanFile, CMake, tools


class SbpConan(ConanFile):
    name = "sbp"
    license = "MIT"
    homepage = "https://github.com/swift-nav/libsbp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Swift Binary Protocol client library"
    topics = ("gnss",)
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    exports = "submoduledata.yml"
    exports_sources = "CMakeLists.txt", "c"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder
        )

        submodule_filename = os.path.join(self.recipe_folder, "submoduledata.yml")
        with open(submodule_filename, "r") as submodule_stream:
            submodules_data = yaml.load(submodule_stream)
            for path, submodule in submodules_data["submodules"][self.version].items():
                submodule_data = {
                    "url": submodule["url"],
                    "sha256": submodule["sha256"],
                    "destination": os.path.join(self._source_subfolder, path),
                    "strip_root": True,
                }
                tools.get(**submodule_data)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["libsbp_ENABLE_TESTS"] = "OFF"
        self._cmake.definitions["libsbp_ENABLE_DOCS"] = "OFF"
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self.copy(
            "LICENSE",
            src=self._source_subfolder,
            dst="licenses",
            ignore_case=True,
            keep_path=False,
        )
        self._configure_cmake().install()

    def package_info(self):
        self.cpp_info.libs = ["sbp"]
