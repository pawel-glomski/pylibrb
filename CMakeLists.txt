cmake_minimum_required(VERSION 3.18)

project(pylibrb)

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
   $ python setup.py install
  =====================================================================")
endif()

# Create CMake targets for Python components needed by nanobind
find_package(Python 3.8 COMPONENTS Interpreter Development.Module REQUIRED)

if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

# Detect the installed nanobind package and import it into CMake
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE NB_DIR)
list(APPEND CMAKE_PREFIX_PATH "${NB_DIR}")

find_package(nanobind CONFIG REQUIRED)


set(SOURCES_DIR "${CMAKE_SOURCE_DIR}/src")

set(THIRD_PARTY_DIR "${CMAKE_SOURCE_DIR}/3rdparty")

set(RUBBERBAND_DIR "${THIRD_PARTY_DIR}/rubberband")
set(RUBBERBAND_INCLUDE_DIR "${RUBBERBAND_DIR}")
set(RUBBERBAND_HEADER_LIST
  "${RUBBERBAND_INCLUDE_DIR}/rubberband/RubberBandStretcher.h"
)
set(RUBBERBAND_SOURCE_LIST
  "${RUBBERBAND_DIR}/single/RubberBandSingle.cpp"
)

set(HEADER_LIST
  ${RUBBERBAND_HEADER_LIST}
)
set(SOURCE_LIST 
  "${SOURCES_DIR}/bindings.cpp"
  ${RUBBERBAND_SOURCE_LIST}
)

nanobind_add_module(pylibrb_ext ${HEADER_LIST} ${SOURCE_LIST})
target_include_directories(pylibrb_ext 
  PUBLIC ${RUBBERBAND_INCLUDE_DIR}
)

# Install directive for scikit-build
install(TARGETS pylibrb_ext LIBRARY DESTINATION .)
