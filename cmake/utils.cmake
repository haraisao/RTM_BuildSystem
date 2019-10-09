# Dissect the version specified in PROJECT_VERSION, placing the major,
# minor, revision and candidate components in PROJECT_VERSION_MAJOR, etc.
# _prefix: The prefix string for the version variable names.
macro(DISSECT_VERSION)
    # Find version components
    string(REGEX REPLACE "^([0-9]+).*" "\\1"
        PROJECT_VERSION_MAJOR "${PROJECT_VERSION}")
    string(REGEX REPLACE "^[0-9]+\\.([0-9]+).*" "\\1"
        PROJECT_VERSION_MINOR "${PROJECT_VERSION}")
    string(REGEX REPLACE "^[0-9]+\\.[0-9]+\\.([0-9]+)" "\\1"
        PROJECT_VERSION_REVISION "${PROJECT_VERSION}")
    string(REGEX REPLACE "^[0-9]+\\.[0-9]+\\.[0-9]+(.*)" "\\1"
        PROJECT_VERSION_CANDIDATE "${PROJECT_VERSION}")
endmacro(DISSECT_VERSION)

# Filter a list to remove all strings matching the regex in _pattern. The
# output is placed in the variable pointed at by _output.
macro(FILTER_LIST _list _pattern _output)
    set(${_output})
    foreach(_item ${${_list}})
        if("${_item}" MATCHES ${_pattern})
            set(${_output} ${${_output}} ${_item})
        endif("${_item}" MATCHES ${_pattern})
    endforeach(_item)
endmacro(FILTER_LIST)

#
#
macro(DecomposeRtmVersion)
  string(REGEX REPLACE "^([0-9]+).*" "\\1"
        OPENRTM_VERSION_MAJOR "${OPENRTM_VERSION}")
  string(REGEX REPLACE "^[0-9]+\\.([0-9]+).*" "\\1"
        OPENRTM_VERSION_MINOR "${OPENRTM_VERSION}")
  string(REGEX REPLACE "^[0-9]+\\.[0-9]+\\.([0-9]+)" "\\1"
        OPENRTM_VERSION_PATCH "${OPENRTM_VERSION}")
  set(OPENRTM_SHORT_VERSION ${OPENRTM_VERSION_MAJOR}${OPENRTM_VERSION_MINOR}${OPENRTM_VERSION_PATCH})
endmacro(DecomposeRtmVersion)
#
#
macro(MAP_ADD_STR _list _str _output)
    set(${_output})
    #message("==== ${${_list}}")
    foreach(_item ${${_list}})
        #message(${${_output}} ${_str}${_item})
        set(${_output} ${${_output}} ${_str}${_item})
    endforeach(_item)
endmacro(MAP_ADD_STR)

#
#
function(get_dist ARG0)
 if(NOT ${CMAKE_SYSTEM_NAME} MATCHES "Linux")
   set(${ARG0} ${CMAKE_SYSTEM_NAME} PARENT_SCOPE)
   return()
 endif()
 foreach(dist Debian Ubuntu RedHat Fedora CentOS Raspbian)
   execute_process(
     COMMAND grep ${dist} -s /etc/issue /etc/os-release /etc/redhat-release /etc/system-release
     OUTPUT_VARIABLE dist_name
     )
   if(${dist_name} MATCHES ${dist})
     set(${ARG0} ${dist} PARENT_SCOPE)
     return()
   endif()
 endforeach()
endfunction(get_dist)

#
#
function(get_pkgmgr ARG0)
 get_dist(DIST_NAME)
 MESSAGE(STATUS "Distribution is ${DIST_NAME}")
 if(${DIST_NAME} MATCHES "Debian" OR
     ${DIST_NAME} MATCHES "Ubuntu" OR
     ${DIST_NAME} MATCHES "Raspbian")
    set(${ARG0} "DEB" PARENT_SCOPE)
    return()
 endif()
 if(${DIST_NAME} MATCHES "RedHat" OR
    ${DIST_NAME} MATCHES "Fedora" OR
    ${DIST_NAME} MATCHES "CentOS")
    set(${ARG0} "RPM" PARENT_SCOPE)
    return()
 endif()
endfunction(get_pkgmgr)

#
#
macro(CheckPkgManager)
  get_pkgmgr(PKGMGR)
  if(PKGMGR AND NOT LINUX_PACKAGE_GENERATOR)
    set(LINUX_PACKAGE_GENERATOR ${PKGMGR})
    if(${PKGMGR} MATCHES "DEB")
      execute_process(COMMAND dpkg --print-architecture
        OUTPUT_VARIABLE CPACK_DEBIAN_PACKAGE_ARCHITECTURE
        OUTPUT_STRIP_TRAILING_WHITESPACE)
      message(STATUS "Package manager is ${PKGMGR}. Arch is ${CPACK_DEBIAN_PACKAGE_ARCHITECTURE}.")
    elseif(${PKGMGR} MATCHES "RPM")
      execute_process(COMMAND uname "-m"
        OUTPUT_VARIABLE CPACK_RPM_PACKAGE_ARCHITECTURE
        OUTPUT_STRIP_TRAILING_WHITESPACE)
      message(STATUS "Package manager is ${PKGMGR}. Arch is ${CPACK_RPM_PACKAGE_ARCHITECTURE}.")
    endif()
  endif()
endmacro(CheckPkgManager)

macro(AddUninstallTarget)
  CONFIGURE_FILE ("${OPENRTM_DIR}/../cmake/uninstall_target.cmake.in"
    "${PROJECT_BINARY_DIR}/uninstall_target.cmake" IMMEDIATE @ONLY)
  ADD_CUSTOM_TARGET (${PROJECT_NAME}_uninstall "${CMAKE_COMMAND}" -P
    "${PROJECT_BINARY_DIR}/uninstall_target.cmake")
endmacro(AddUninstallTarget)

macro(CreatePackageCPack)
  IF(NOT DEFINED CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_NO_WARNINGS)
    SET(CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_NO_WARNINGS ON)
  ENDIF()

  include(InstallRequiredSystemLibraries)
  set(PROJECT_EXECUTABLES ${PROJECT_NAME}Comp "${PROJECT_NAME}Comp.exe")

  set(cpack_options "${PROJECT_BINARY_DIR}/cpack_options.cmake")

  configure_file("${OPENRTM_DIR}/cmake/cpack_options.cmake.in"
    ${cpack_options} @ONLY)

  set(CPACK_PROJECT_CONFIG_FILE ${cpack_options})
  include(${CPACK_PROJECT_CONFIG_FILE})
  include(CPack)
endmacro(CreatePackageCPack)


macro(SetupInstDirs)
  if (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(CMAKE_CXX_COMPILER "g++")
    set(CMAKE_MACOSX_RPATH 1)
  endif()

  if(WIN32)
    set(OPENRTM_SHARE_PREFIX "OpenRTM-aist/Components/${PROJECT_TYPE}")
    set(INSTALL_PREFIX ${PROJECT_NAME})
    if (CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
      set(CMAKE_INSTALL_PREFIX "${OPENRTM_DIR}/Components/${PROJECT_TYPE}" CACHE PATH "..." FORCE)
    endif()
  else()
    set(OPENRTM_SHARE_PREFIX "/share/openrtm-${OPENRTM_VERSION_MAJOR}.${OPENRTM_VERSION_MINOR}")
    set(INSTALL_PREFIX "${OPENRTM_SHARE_PREFIX}/components/${PROJECT_TYPE}")
  endif()
endmacro(SetupInstDirs)

#
# check drive letter
function(localPath path outpath)
  if(EXISTS path)
    set(${out}path ${path} PARENT_SCOPE)
  else()
    if (WIN32)
      get_filename_component(MyROOT ${CMAKE_CURRENT_SOURCE_DIR} ABSOLUTE)
      string(SUBSTRING ${MyROOT} 0 2 CURRENT_DRIVE)
      string(REGEX REPLACE "^[A-Z,a-z]:" ${CURRENT_DRIVE} out ${path})
      set(${outpath} ${out} PARENT_SCOPE)
    else()
      set(${out}path ${path} PARENT_SCOPE)
    endif()
  endif()
endfunction()