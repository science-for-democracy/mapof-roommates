from setuptools import setup 
from pybind11.setup_helpers import Pybind11Extension, build_ext

cpp_dist_module = Pybind11Extension('mapel.elections.distances.cppdistances',
['src/mapel/elections/distances/cppdistances.cpp'], extra_compile_args=["-Ofast"])

setup(
  ext_modules = [cpp_dist_module],
  cmdclass={"build_ext": build_ext},
)
