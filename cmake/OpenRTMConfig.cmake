
# -*- cmake -*-
#
# @file OpenRTMConfig.cmake
# @brief cmake-config file for OpenRTM-aist on Windows
# @date Fri Aug 16 15:04:09 2019 
#
# This file is used for cmake config-mode.
# The following variables are defined.
#
# Basic compiler/linker options
# - OPENRTM_CFLAGS: cflags 
# - OPENRTM_INCLUDE_DIRS: include directories
# - OPENRTM_LDFLAGS: linker options
# - OPENRTM_LIBRARY_DIRS: library directories
# - OPENRTM_LIBRARIES: libraries
# - OPENRTM_LIB_DIR: OpenRTM's lib directory
#
# OpenRTM-aist specific directory
# - COIL_INCLUDE_DIR: coil include dir
# - RTM_CAMERA_INCLUDE_DIR: rtmCamera include dir
# - RTM_CAMERA_LIB_DIR: rtmCamera's lib directory
# - RTM_CAMERA_LIBRARIES: rtmCamera libraries
# - RTM_MANIPULATOR_INCLUDE_DIR: rtmManipulator include dir
# - RTM_MANIPULATOR_LIB_DIR: rtmManipulator's lib directory
# - RTM_MANIPULATOR_LIBRARIES: rtmManipulator libraries
#
# OpenRTM-aist version
# - OPENRTM_VERSION: x.y.z version
# - OPENRTM_VERSION_MAJOR: major version number
# - OPENRTM_VERSION_MINOR: minor version number
# - OPENRTM_VERSION_PATCH: revision number
# - OPENRTM_SHORT_VERSION: short version number 1.1.0->110
#
# OpenRTM-aist's CORBA related settings
# - OPENRTM_ORB: CORBA implementation
# - OPENRTM_IDL_WRAPPER: rtm-skelwrapper command
# - OPENRTM_IDL_WRAPPER_FLAGS: rtm-skelwrapper flag
# - OPENRTM_IDLC: IDL command
# - OPENRTM_IDLFLAGS: IDL optins

if(NOT NO_INFO)
  message(STATUS "OpenRTMConfig.cmake found.")
  message(STATUS "Configrued by configuration mode.")
endif()

include("${CMAKE_CURRENT_LIST_DIR}/utils.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/rtc_build.cmake")

include("${CMAKE_CURRENT_LIST_DIR}/vc_version.cmake")

get_vc_version(RTM_VC_VER VC_ARCH)

# OpenRTM-aist version
if(NOT RTM_VC_VER)
  set(RTM_VC_VER $ENV{RTM_VC_VERSION})
  set(VC_ARCH "x64")
endif()

if (NOT OPENRTM_VERSION)
  set(OPENRTM_VERSION 1.2.0)
  #set(OPENRTM_VERSION_MAJOR 1)
  #set(OPENRTM_VERSION_MINOR 2)
  #set(OPENRTM_VERSION_PATCH 0)
  #set(OPENRTM_SHORT_VERSION ${OPENRTM_VERSION_MAJOR}${OPENRTM_VERSION_MINOR}${OPENRTM_VERSION_PATCH})
endif()

DecomposeRtmVersion()
set(RTM_DLLVER ${OPENRTM_SHORT_VERSION}_${RTM_VC_VER}_${VC_ARCH})
set(COIL_DLLVER ${OPENRTM_SHORT_VERSION}_${RTM_VC_VER}_${VC_ARCH})

find_package(omniORB REQUIRED)

# Basic compiler/linker options
get_filename_component(OPENRTM_DIR "${CMAKE_CURRENT_LIST_DIR}/../${OPENRTM_VERSION}" ABSOLUTE)
set(OPENRTM_CFLAGS ${OMNIORB_CFLAGS};-DINCLUDE_stub_in_nt_dll;-DRTC_CORBA_CXXMAPPING11;-D_WIN32_WINNT=0x0500)
set(OPENRTM_INCLUDE_DIRS ${OPENRTM_DIR};${OPENRTM_DIR}/rtm/idl;${OPENRTM_DIR}/rtm/ext)
set(OPENRTM_LDFLAGS )

set(OPENRTM_BIN_PATH "${OPENRTM_DIR}/bin/${VC_VER}")
find_library(RTM_LIBS NAMES RTC${RTM_DLLVER}  coil${COIL_DLLVER}  PATHS ${OPENRTM_BIN_PATH})
if(RTM_LIBS)
  if(NOT NO_INFO)
    message(STATUS "OPENRTM_BIN_PATH=${OPENRTM_BIN_PATH}")
  endif()
else()
  message(ERROR "OpenRTM Libiraris not found")
endif()

# rtmCamera options
set(RTM_CAMERA_INCLUDE_DIR "${OPENRTM_DIR}/rtm/idl")
set(RTM_CAMERA_LIB_DIR "${OPENRTM_BIN_PATH}")
set(RTM_CAMERA_LIBRARIES optimized;rtmCamera${RTM_DLLVER};debug;rtmCamera${RTM_DLLVER}d)

# rtmManipulator options
set(RTM_MANIPULATOR_INCLUDE_DIR "${OPENRTM_DIR}/rtm/idl")
set(RTM_MANIPULATOR_LIB_DIR "${OPENRTM_BIN_PATH}")
set(RTM_MANIPULATOR_LIBRARIES optimized;rtmManipulator${RTM_DLLVER};debug;rtmManipulator${RTM_DLLVER}d)

set(OPENRTM_LIBRARY_DIRS ${OPENRTM_BIN_PATH};${OMNIORB_DIR}/lib/x86_win32)
set(OPENRTM_LIBRARIES optimized;RTC${RTM_DLLVER};optimized;coil${COIL_DLLVER};optimized;advapi32;optimized;ws2_32;optimized;mswsock;debug;RTC${RTM_DLLVER}d;debug;coil${COIL_DLLVER}d;debug;advapi32;debug;ws2_32;debug;mswsock;${OMNIORB_LIBRARIES};${RTM_CAMERA_LIBRARIES};${RTM_MANIPULATOR_LIBRARIES})

# OpenRTM-aist specific directory
set(COIL_INCLUDE_DIR ${OPENRTM_DIR}/bin)

# OpenRTM-aist's CORBA related settings
set(OPENRTM_ORB omniORB)
set(OPENRTM_IDL_WRAPPER rtm-skelwrapper.py)
set(OPENRTM_IDL_WRAPPER_FLAGS --include-dir="";--skel-suffix=Skel;--stub-suffix=Stub)
set(OPENRTM_IDLC omniidl)
set(OPENRTM_IDLFLAGS -bcxx;-Wba;-nf;-Wbshortcut;-I${OPENRTM_DIR}/rtm/idl)

#
#
if(STATIC_LIBS)
    set(LIB_TYPE STATIC)
else(STATIC_LIBS)
    set(LIB_TYPE SHARED)
endif(STATIC_LIBS)

#
#
if(NOT NO_INFO)
  message(STATUS "OpenRTM-aist configuration done")

  message(STATUS "  OMNIORB_DIR=${OMNIORB_DIR}")
  message(STATUS "  OMNIORB_VERSION=${OMNIORB_VERSION}")
  message(STATUS "  OMNIORB_CFLAGS=${OMNIORB_CFLAGS}")
  message(STATUS "  OMNIORB_INCLUDE_DIRS=${OMNIORB_INCLUDE_DIRS}")
  message(STATUS "  OMNIORB_LDFLAGS=${OMNIORB_LDFLAGS}")
  message(STATUS "  OMNIORB_LIBRARY_DIRS=${OMNIORB_LIBRARY_DIRS}")
  message(STATUS "  OMNIORB_LIBRARIES=${OMNIORB_LIBRARIES}")

  message(STATUS "  RTM_CAMERA_INCLUDE_DIR=${RTM_CAMERA_INCLUDE_DIR}")
  message(STATUS "  RTM_CAMERA_LIB_DIR=${RTM_CAMERA_LIB_DIR}")
  message(STATUS "  RTM_CAMERA_LIBRARIES=${RTM_CAMERA_LIBRARIES}")
  message(STATUS "  RTM_MANIPULATOR_INCLUDE_DIR=${RTM_MANIPULATOR_INCLUDE_DIR}")
  message(STATUS "  RTM_MANIPULATOR_LIB_DIR=${RTM_MANIPULATOR_LIB_DIR}")
  message(STATUS "  RTM_MANIPULATOR_LIBRARIES=${RTM_MANIPULATOR_LIBRARIES}")

  message(STATUS "  OPENRTM_DIR=${OPENRTM_DIR}")
  message(STATUS "  OPENRTM_VERSION=${OPENRTM_VERSION}")
  message(STATUS "  OPENRTM_VERSION_MAJOR=${OPENRTM_VERSION_MAJOR}")
  message(STATUS "  OPENRTM_VERSION_MINOR=${OPENRTM_VERSION_MINOR}")
  message(STATUS "  OPENRTM_VERSION_PATCH=${OPENRTM_VERSION_PATCH}")
  message(STATUS "  OPENRTM_CFLAGS=${OPENRTM_CFLAGS}")
  message(STATUS "  OPENRTM_INCLUDE_DIRS=${OPENRTM_INCLUDE_DIRS}")
  message(STATUS "  OPENRTM_LDFLAGS=${OPENRTM_LDFLAGS}")
  message(STATUS "  OPENRTM_LIBRARY_DIRS=${OPENRTM_LIBRARY_DIRS}")
  message(STATUS "  OPENRTM_LIBRARIES=${OPENRTM_LIBRARIES}")

  message(STATUS "  OPENRTM_IDLC=${OPENRTM_IDLC}")
  message(STATUS "  OPENRTM_IDLFLAGS=${OPENRTM_IDLFLAGS}")
  message(STATUS "  OPENRTM_IDL_WRAPPER=${OPENRTM_IDL_WRAPPER}")
  message(STATUS "  OPENRTM_IDL_WRAPPER_FLAGS=${OPENRTM_IDL_WRAPPER_FLAGS}")
endif()

#
# Check Distribution and Package Manager
CheckPkgManager()

# Set up installation directories
SetupInstDirs()

# end of OpenRTMConfig.cmake