cmake_minimum_required(VERSION 3.26)

if (NOT DEFINED CMAKE_BUILD_TYPE)
    message(WARNING "\
        CMAKE_BUILD_TYPE should be defined and it must match `cmake.build-type`. We will try to
        build the Release version...")
    set(CMAKE_BUILD_TYPE "Release")
    # This is important: CMake will change the order of paths that `pkg_check_modules` uses to find
    # libraries. pylibrb extension must link to the same windows runtime libraries as the found
    # Rubberbind library, so their build types must match.
endif()

project(pylibrb LANGUAGES CXX)

if (NOT SKBUILD)
  message(WARNING "\
  This CMake file is meant to be executed using 'scikit-build'. Running
  it directly will almost certainly not produce the desired result. If
  you are a user trying to install this package, please use the command
  below, which will install all necessary build dependencies, compile
  the package in an isolated environment, and then install it.
  =====================================================================
   $ pip install .
  =====================================================================
  If you are a software developer, and this is your own package, then
  it is usually much more efficient to install the build dependencies
  in your environment once and use the following command that avoids
  a costly creation of a new virtual environment at every compilation:
  =====================================================================
   $ pip install nanobind scikit-build-core[pyproject]
   $ pip install --no-build-isolation -ve .
  =====================================================================
  You may optionally add -Ceditable.rebuild=true to auto-rebuild when
  the package is imported. Otherwise, you need to re-run the above
  after editing C++ files.")
endif()

if (DEFINED CMAKE_TOOLCHAIN_FILE)
    message(STATUS "Using a toolchain: ${CMAKE_TOOLCHAIN_FILE}")
endif()

# Try to import all Python components potentially needed by nanobind
find_package(Python 3.8
  REQUIRED COMPONENTS Interpreter Development.Module
  OPTIONAL_COMPONENTS Development.SABIModule)

# Import nanobind through CMake's find_package mechanism
find_package(nanobind CONFIG REQUIRED)

add_subdirectory(src)
