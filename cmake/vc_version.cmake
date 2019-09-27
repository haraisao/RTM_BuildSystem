#
#
macro(get_vc_version _vc_version _vc_arch)
if (${MSVC_VERSION} GREATER 1919 AND ${MSVC_VERSION} LESS 1930)
  set(${_vc_version} "vc14")

elseif (${MSVC_VERSION} GREATER 1909 AND ${MSVC_VERSION} LESS 1920)
  set(${_vc_version} "vc14")

elseif (${MSVC_VERSION} EQUAL 1900)
  set(${_vc_version} "vc14")

elseif (${MSVC_VERSION} EQUAL 1800)
  set(${_vc_version} "vc12")

elseif (${MSVC_VERSION} EQUAL 1700)
  set(${_vc_version} "vc11")

elseif (${MSVC_VERSION} EQUAL 1600)
  set(${_vc_version} "vc10")

else ()
   set(${_vc_version} "vc9")
endif()

if ("${CMAKE_GENERATOR_PLATFORM}" STREQUAL "x64"  OR "${CMAKE_GENERATOR}" MATCHES "Win64")
  set(${_vc_arch} "x64")
else()
  set(${_vc_arch} "x86")
endif()
endmacro(get_vc_version)