####################################################################################################
# 3rdparty

set(CMAKE_POSITION_INDEPENDENT_CODE On) # for fmt
add_subdirectory("${CMAKE_SOURCE_DIR}/3rdparty/fmt" "3rdparty/fmt" EXCLUDE_FROM_ALL)

####################################################################################################
# bindings

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

target_link_libraries(pylibrb_ext PRIVATE
  fmt::fmt
)

if(APPLE)
  target_link_libraries(pylibrb_ext PRIVATE "-framework Accelerate")
endif()

if(WIN32)
  target_compile_definitions(pylibrb_ext PRIVATE NOMINMAX)
endif()

target_include_directories(pylibrb_ext 
  PUBLIC ${RUBBERBAND_INCLUDE_DIR}
)

# Install directive for scikit-build
install(TARGETS pylibrb_ext LIBRARY DESTINATION .)
