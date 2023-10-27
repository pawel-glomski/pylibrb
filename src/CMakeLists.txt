####################################################################################################
# 3rdparty

find_package(fmt CONFIG REQUIRED)
find_package(PkgConfig)
pkg_check_modules(rubberband REQUIRED IMPORTED_TARGET rubberband)

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
    PRIVATE
    fmt::fmt
    PkgConfig::rubberband
)

if(APPLE)
  target_link_libraries(pylibrb_ext PRIVATE "-framework Accelerate")
endif()

if(WIN32)
  target_compile_definitions(pylibrb_ext PRIVATE NOMINMAX)
endif()


# Install directive for scikit-build
install(TARGETS pylibrb_ext LIBRARY DESTINATION pylibrb)
