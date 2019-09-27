#
#
if(NOT NO_INFO)
  message("==== omniORB Config ===")
endif()
set(OMNIORB_FOUND  False)

include("${CMAKE_CURRENT_LIST_DIR}/vc_version.cmake")

get_vc_version(VC_VER VC_ARCH)

get_filename_component(OMNIORB_DIR "${CMAKE_CURRENT_LIST_DIR}/4.2.3_${VC_VER}" ABSOLUTE)

#
#
#find_path(OMNIORB_DIR lib/x86_win32/omniORB4.lib
#            HINTS $ENV{ORB_ROOT_DIR})
if(NOT NO_INFO)
  message("omniORB_Root: ${OMNIORB_DIR}")
endif()

#
#
set(OMNI_BIN_DIR ${OMNIORB_DIR}/bin/x86_win32 )
find_file(OMNIIDL omniidl.exe
            HINTS ${OMNI_BIN_DIR})

#
#
if( OMNIORB_DIR AND OMNIIDL)
    set(OMNIORB_FOUND True)
    if(NOT NO_INFO)
      message("IDL Compiler: ${OMNIIDL}")
    endif()
    set(OMNIORB_VERSION 4.2.3)
    set(OMNI_DLLVER 423)
    set(OMNITHREAD_DLLVER 41)
    set(OMNIORB_INCLUDE_DIRS  ${OMNIORB_DIR}/include)
    set(OMNIORB_LIBRARY_DIRS ${OMNIORB_DIR}/lib/x86_win32 )
    set(OMNIORB_CFLAGS "-D__WIN32__ -D__NT__ -D__OSVERSION__=4 -D__x86__ -D_WIN32_WINNT=0x0400 -D_CRT_SECURE_NO_DEPRECATE")
    set(OMNIORB_LIBRARIES optimized;omniORB${OMNI_DLLVER}_rt;optimized;omniDynamic${OMNI_DLLVER}_rt;optimized;omnithread${OMNITHRED_DLLVER}_rt;debug;omniORB${OMNI_DLLVER}_rt;debug;omniDynamic${OMNI_DLLVER}_rt;debug;omnithread${OMNITHRED_DLLVER}_rtd)
endif()