#
# for build component
#

#
# IDL FILE
macro(add_idl_files)
  if (${ARGC} GREATER 0)
    #message("--- Set IDFILE: ${ARGN}")
    #include("${OPENRTM_DIR}/cmake/idl_compile.cmake")
    set(idls )
    foreach(itm ${ARGN})
      list(APPEND IDL_FILES  "${CMAKE_CURRENT_SOURCE_DIR}/${itm}")
    endforeach()
  endif()
endmacro(add_idl_files)

#
#
macro(compile_idl_files)
  OPENRTM_COMPILE_IDL_FILES(${IDL_FILES})
  FILTER_LIST("ALL_IDL_SRCS" "hh$" idl_headers)
  include_directories( ${PROJECT_BINARY_DIR}/idl )
  set_source_files_properties(${ALL_IDL_SRCS} PROPERTIES GENERATED 1)
  if(NOT TARGET ALL_IDL_TGT)
   add_custom_target(ALL_IDL_TGT)
  endif()
endmacro(compile_idl_files)
#
#
#
macro(RewriteBuildOptions)
  if(${OPENRTM_VERSION_MAJOR} LESS 2)
    set(OPENRTM_CFLAGS ${OPENRTM_CFLAGS} ${OMNIORB_CFLAGS})
    set(OPENRTM_INCLUDE_DIRS ${OPENRTM_INCLUDE_DIRS} ${OMNIORB_INCLUDE_DIRS})
    set(OPENRTM_LIBRARY_DIRS ${OPENRTM_LIBRARY_DIRS} ${OMNIORB_LIBRARY_DIRS})
  endif()

  if (WIN32)
    if(USE_UTF8)
      set(OPENRTM_CFLAGS "${OPENRTM_CFLAGS} /utf-8 /wd4996")
    else()
      set(OPENRTM_CFLAGS "${OPENRTM_CFLAGS}  /wd4996")
    endif()
  endif()

  if (DEFINED OPENRTM_INCLUDE_DIRS)
    string(REGEX REPLACE "-I" ";"
      OPENRTM_INCLUDE_DIRS "${OPENRTM_INCLUDE_DIRS}")
    string(REGEX REPLACE " ;" ";"
      OPENRTM_INCLUDE_DIRS "${OPENRTM_INCLUDE_DIRS}")
  endif (DEFINED OPENRTM_INCLUDE_DIRS)

  if (DEFINED OPENRTM_LIBRARY_DIRS)
    string(REGEX REPLACE "-L" ";"
      OPENRTM_LIBRARY_DIRS "${OPENRTM_LIBRARY_DIRS}")
    string(REGEX REPLACE " ;" ";"
      OPENRTM_LIBRARY_DIRS "${OPENRTM_LIBRARY_DIRS}")
  endif (DEFINED OPENRTM_LIBRARY_DIRS)

  if (DEFINED OPENRTM_LIBRARIES)
    string(REGEX REPLACE "-l" ";"
      OPENRTM_LIBRARIES "${OPENRTM_LIBRARIES}")
    string(REGEX REPLACE " ;" ";"
      OPENRTM_LIBRARIES "${OPENRTM_LIBRARIES}")
  endif (DEFINED OPENRTM_LIBRARIES)
endmacro(RewriteBuildOptions)


macro(add_rtc_library)
  math(EXPR arg_len "${ARGC}-1")
  set(_src ${ARGN})
  list(SUBLIST _src 1 ${arg_len} srcs)
  add_library(${ARGV0} ${LIB_TYPE} ${srcs})
  set_target_properties(${ARGV0} PROPERTIES PREFIX "")
  if(TARGET ALL_IDL_TGT)
    add_dependencies(${ARGV0} ALL_IDL_TGT)
  endif()
  target_link_libraries(${ARGV0} ${OPENRTM_LIBRARIES} ${OPTION_LIBRARIES})
endmacro(add_rtc_library)


macro(add_rtc_executable)
  math(EXPR arg_len "${ARGC}-1")
  set(_src ${ARGN})
  list(SUBLIST _src 1 ${arg_len} srcs)
  add_executable(${ARGV0} ${srcs})
  if(TARGET ALL_IDL_TGT)
    add_dependencies(${ARGV0} ALL_IDL_TGT)
  endif()
  target_link_libraries(${ARGV0} ${OPENRTM_LIBRARIES} ${OPTION_LIBRARIES})
endmacro(add_rtc_executable)

macro(gen_setup_bat)
 set (CMAKE_BIN_PATH $ENV{CMAKE_BIN_PATH})
 set (PYTHON_DIR $ENV{PYTHON_DIR})
 configure_file(${OPENRTM_DIR}/../cmake/setup.bat.in ${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/setup.bat @ONLY)
 install(FILES ${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/setup.bat DESTINATION bin)
endmacro(gen_setup_bat)