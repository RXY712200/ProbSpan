cmake_minimum_required(VERSION 3.16)
project(ProbSpan VERSION 1.0.0 LANGUAGES C)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
option(PROBSPAN_BUILD_EXAMPLES "Build examples using the public API" OFF)

add_library(probspan STATIC
  src/probspan.c
  src/subjective.c
  src/odds.c
  src/decimal.c
  src/historical.c
  src/beta.c
  src/gamma.c
  src/beta_logit.c
  src/decision_geometry.c
  src/decision_policy.c
  src/subjective_analysis.c
  src/historical_analysis.c
  src/provenance.c
  src/analysis_composition.c
)
target_compile_features(probspan PUBLIC c_std_11)
set_target_properties(probspan PROPERTIES C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
add_library(ProbSpan::probspan ALIAS probspan)
target_include_directories(probspan PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)
if(NOT MSVC)
  target_link_libraries(probspan PUBLIC m)
endif()

install(TARGETS probspan EXPORT ProbSpanTargets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY include/probspan DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
set(PROBSPAN_PACKAGE_DIR ${CMAKE_INSTALL_LIBDIR}/cmake/ProbSpan)
configure_package_config_file(cmake/ProbSpanConfig.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/ProbSpanConfig.cmake
  INSTALL_DESTINATION ${PROBSPAN_PACKAGE_DIR})
write_basic_package_version_file(${CMAKE_CURRENT_BINARY_DIR}/ProbSpanConfigVersion.cmake
  VERSION ${PROJECT_VERSION} COMPATIBILITY SameMajorVersion)
install(EXPORT ProbSpanTargets NAMESPACE ProbSpan:: DESTINATION ${PROBSPAN_PACKAGE_DIR})
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/ProbSpanConfig.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/ProbSpanConfigVersion.cmake DESTINATION ${PROBSPAN_PACKAGE_DIR})

if(PROBSPAN_BUILD_EXAMPLES)
  add_executable(probspan_decision_example examples/decision.c)
  add_executable(probspan_provenance_example examples/provenance.c)
  target_link_libraries(probspan_decision_example PRIVATE ProbSpan::probspan)
  target_link_libraries(probspan_provenance_example PRIVATE ProbSpan::probspan)
endif()

if(MSVC)
  target_compile_options(probspan PRIVATE /W4)
else()
  target_compile_options(probspan PRIVATE -Wall -Wextra -Wpedantic)
endif()

include(CTest)
if(BUILD_TESTING)
  if(PROBSPAN_BUILD_EXAMPLES)
    add_test(NAME probspan_decision_example COMMAND probspan_decision_example)
    add_test(NAME probspan_provenance_example COMMAND probspan_provenance_example)
  endif()
  add_executable(probspan_smoke tests/smoke.c)
  set_target_properties(probspan_smoke PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_link_libraries(probspan_smoke PRIVATE probspan)
  add_test(NAME probspan_smoke COMMAND probspan_smoke)

  add_executable(probspan_api_contract tests/api_contract.c)
  target_link_libraries(probspan_api_contract PRIVATE probspan)
  set_target_properties(probspan_api_contract PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  if(MSVC)
    target_compile_options(probspan_api_contract PRIVATE /W4)
  else()
    target_compile_options(probspan_api_contract PRIVATE -Wall -Wextra -Wpedantic)
  endif()
  add_test(NAME probspan_api_contract COMMAND probspan_api_contract)

  add_executable(probspan_oracle_parity tests/oracle_parity.c)
  target_link_libraries(probspan_oracle_parity PRIVATE probspan)
  target_include_directories(probspan_oracle_parity PRIVATE src tests)
  set_target_properties(probspan_oracle_parity PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  if(MSVC)
    target_compile_options(probspan_oracle_parity PRIVATE /W4)
  else()
    target_compile_options(probspan_oracle_parity PRIVATE -Wall -Wextra -Wpedantic)
  endif()
  add_test(NAME probspan_oracle_parity COMMAND probspan_oracle_parity)

  add_executable(probspan_large_numerics tests/large_numerics.c)
  target_link_libraries(probspan_large_numerics PRIVATE probspan)
  target_include_directories(probspan_large_numerics PRIVATE src tests)
  set_target_properties(probspan_large_numerics PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  if(MSVC)
    target_compile_options(probspan_large_numerics PRIVATE /W4)
  else()
    target_compile_options(probspan_large_numerics PRIVATE -Wall -Wextra -Wpedantic)
  endif()
  add_test(NAME probspan_large_numerics COMMAND probspan_large_numerics)

  add_executable(probspan_decimal_parity tests/decimal_parity.c)
  target_link_libraries(probspan_decimal_parity PRIVATE probspan)
  target_include_directories(probspan_decimal_parity PRIVATE src tests)
  set_target_properties(probspan_decimal_parity PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  if(MSVC)
    target_compile_options(probspan_decimal_parity PRIVATE /W4)
  else()
    target_compile_options(probspan_decimal_parity PRIVATE -Wall -Wextra -Wpedantic)
  endif()
  add_test(NAME probspan_decimal_parity COMMAND probspan_decimal_parity)

  add_executable(probspan_analysis_parity tests/analysis_parity.c)
  target_link_libraries(probspan_analysis_parity PRIVATE probspan)
  target_include_directories(probspan_analysis_parity PRIVATE tests)
  set_target_properties(probspan_analysis_parity PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  if(MSVC)
    target_compile_options(probspan_analysis_parity PRIVATE /W4)
  else()
    target_compile_options(probspan_analysis_parity PRIVATE -Wall -Wextra -Wpedantic)
  endif()
  add_test(NAME probspan_analysis_parity COMMAND probspan_analysis_parity)

  find_package(Python3 COMPONENTS Interpreter QUIET)
  add_executable(probspan_state_parity tests/state_parity.c)
  target_link_libraries(probspan_state_parity PRIVATE probspan)
  target_include_directories(probspan_state_parity PRIVATE tests)
  set_target_properties(probspan_state_parity PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  if(MSVC)
    target_compile_options(probspan_state_parity PRIVATE /W4)
  else()
    target_compile_options(probspan_state_parity PRIVATE -Wall -Wextra -Wpedantic)
  endif()
  add_test(NAME probspan_state_parity COMMAND probspan_state_parity)
  if(Python3_Interpreter_FOUND)
    add_test(NAME probspan_state_fixture_freshness
      COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/generate_state_fixtures.py --check)
    add_test(NAME probspan_fixture_freshness
      COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/generate_fixtures.py --check)
    add_test(NAME probspan_large_fixture_freshness
      COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/generate_large_fixtures.py --check)
    add_test(NAME probspan_decimal_fixture_freshness
      COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/generate_decimal_fixtures.py --check)
    add_test(NAME probspan_analysis_fixture_freshness
      COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/generate_analysis_fixtures.py --check)
  endif()
endif()
