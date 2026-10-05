cmake_minimum_required(VERSION 3.16)
project(ProbSpan VERSION 1.0.0 LANGUAGES C)

add_library(probspan STATIC
  src/probspan.c
  src/subjective.c
  src/odds.c
  src/historical.c
  src/beta.c
)
target_compile_features(probspan PUBLIC c_std_11)
set_target_properties(probspan PROPERTIES C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
target_include_directories(probspan PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)
if(NOT MSVC)
  target_link_libraries(probspan PUBLIC m)
endif()

if(MSVC)
  target_compile_options(probspan PRIVATE /W4)
else()
  target_compile_options(probspan PRIVATE -Wall -Wextra -Wpedantic)
endif()

include(CTest)
if(BUILD_TESTING)
  add_executable(probspan_smoke tests/smoke.c)
  set_target_properties(probspan_smoke PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
  target_link_libraries(probspan_smoke PRIVATE probspan)
  add_test(NAME probspan_smoke COMMAND probspan_smoke)

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

  find_package(Python3 COMPONENTS Interpreter QUIET)
  if(Python3_Interpreter_FOUND)
    add_test(NAME probspan_fixture_freshness
      COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/generate_fixtures.py --check)
  endif()
endif()
