cmake_minimum_required(VERSION 3.16)
project(ProbSpanModels VERSION 2.0.0 LANGUAGES C)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

add_library(probspan_models STATIC src/version.c src/binomial_interval.c)
add_library(ProbSpanModels::models ALIAS probspan_models)
set_target_properties(probspan_models PROPERTIES
  EXPORT_NAME models C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
target_compile_features(probspan_models PUBLIC c_std_11)
target_include_directories(probspan_models PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

if(NOT MSVC)
  target_link_libraries(probspan_models PUBLIC m)
  target_compile_options(probspan_models PRIVATE -fno-fast-math -ffp-contract=off)
else()
  target_compile_options(probspan_models PRIVATE /fp:strict)
endif()

set(package_dir "${CMAKE_INSTALL_LIBDIR}/cmake/ProbSpanModels")
install(TARGETS probspan_models EXPORT ProbSpanModelsTargets
  ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}")
install(FILES include/probspan_models/version.h include/probspan_models/binomial_interval.h
  DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/probspan_models")
configure_package_config_file(cmake/ProbSpanModelsConfig.cmake.in
  "${CMAKE_CURRENT_BINARY_DIR}/ProbSpanModelsConfig.cmake"
  INSTALL_DESTINATION "${package_dir}")
write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/ProbSpanModelsConfigVersion.cmake"
  VERSION "${PROJECT_VERSION}" COMPATIBILITY SameMajorVersion)
install(EXPORT ProbSpanModelsTargets NAMESPACE ProbSpanModels::
  DESTINATION "${package_dir}")
install(FILES
  "${CMAKE_CURRENT_BINARY_DIR}/ProbSpanModelsConfig.cmake"
  "${CMAKE_CURRENT_BINARY_DIR}/ProbSpanModelsConfigVersion.cmake"
  DESTINATION "${package_dir}")

include(CTest)
if(BUILD_TESTING)
  add_executable(models_version_test tests/version.c)
  target_link_libraries(models_version_test PRIVATE ProbSpanModels::models)
  add_test(NAME models_version COMMAND models_version_test)
  add_executable(models_binomial_test tests/binomial_interval.c)
  target_link_libraries(models_binomial_test PRIVATE ProbSpanModels::models)
  add_test(NAME models_binomial COMMAND models_binomial_test)
  add_executable(models_interval_probe tests/interval_probe.c)
  target_link_libraries(models_interval_probe PRIVATE ProbSpanModels::models)
endif()
