cmake_minimum_required(VERSION 3.16)
project(icecream_dashboard)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Qml Quick)

qt_add_executable(icecream_dashboard
  src/main.cpp
  src/FlavorNode.cpp
  src/FlavorNode.h
)

qt_add_qml_module(icecream_dashboard
  URI IceCreamDashboard
  VERSION 1.0
  QML_FILES
    qml/Main.qml
    qml/FlavorButton.qml
    qml/CobotArm.qml
    qml/StatePanel.qml
  RESOURCES
    resources/Vanilla.png
    resources/Chocolate.png
    resources/Mixed.png
)

target_include_directories(icecream_dashboard PRIVATE
  ${rclcpp_INCLUDE_DIRS}
  ${std_msgs_INCLUDE_DIRS}
)

target_link_libraries(icecream_dashboard PRIVATE
  Qt6::Core
  Qt6::Gui
  Qt6::Qml
  Qt6::Quick
  ${rclcpp_LIBRARIES}
  ${std_msgs_LIBRARIES}
)

install(TARGETS icecream_dashboard
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
