cmake_minimum_required(VERSION 3.16)
project(ProbSpanDeviceHistoryConsumer LANGUAGES C)

find_package(ProbSpan 1.0.0 EXACT CONFIG REQUIRED)
add_executable(device-history-v1 v1_consumer.c)
set_target_properties(device-history-v1 PROPERTIES
    C_STANDARD 11 C_STANDARD_REQUIRED YES C_EXTENSIONS NO)
target_link_libraries(device-history-v1 PRIVATE ProbSpan::probspan)
