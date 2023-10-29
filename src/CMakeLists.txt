INCLUDE(CheckLibraryExists)

####################################################################################################
# 3rdparty

find_package(fmt CONFIG REQUIRED)
find_package(PkgConfig)
pkg_check_modules(RUBBERBAND REQUIRED rubberband)

if (WIN32)
    # fftw adds `m` (math.h) to the dependencies for some reason
    message(STATUS "Rubberband's LIBRARIES before: ${RUBBERBAND_LIBRARIES}")
    string(REPLACE ";m;" ";" RUBBERBAND_LIBRARIES "${RUBBERBAND_LIBRARIES}")
    string(REGEX REPLACE ";m$" "" RUBBERBAND_LIBRARIES "${RUBBERBAND_LIBRARIES}")
    message(STATUS "Rubberband's LIBRARIES after: ${RUBBERBAND_LIBRARIES}")
endif()

####################################################################################################
# bindings

set(SOURCES_DIR "${CMAKE_SOURCE_DIR}/src")

set(HEADER_LIST
)
set(SOURCE_LIST 
  "${SOURCES_DIR}/bindings.cpp"
)

nanobind_add_module(
    pylibrb_ext
    STABLE_ABI
    NB_STATIC
    ${HEADER_LIST}
    ${SOURCE_LIST}
)

target_link_libraries(
    pylibrb_ext
    PUBLIC
    fmt::fmt
    ${RUBBERBAND_LIBRARIES}
)

if(APPLE)
  target_link_libraries(pylibrb_ext PRIVATE "-framework Accelerate")
endif()

target_link_directories(
    pylibrb_ext
    PUBLIC
    ${RUBBERBAND_LIBRARY_DIRS}
)
target_include_directories(
    pylibrb_ext
    PUBLIC
    ${RUBBERBAND_INCLUDE_DIRS}
)


if(WIN32)
  target_compile_definitions(pylibrb_ext PRIVATE NOMINMAX)
endif()


# Install directive for scikit-build
install(TARGETS pylibrb_ext LIBRARY DESTINATION pylibrb)
