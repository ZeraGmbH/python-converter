cmake_minimum_required(VERSION 3.1)

project(python-converter LANGUAGES NONE)

message(WARNING "You are building and deploying a python project with cmake.
    To do so is neither common nor safe. This build might fail for following reasons:
    1. python version changed
    2. setuptools pkg name scheme changed
    3. Version changed")

file(GLOB SOURCES
    ${PROJECT_SOURCE_DIR}/*.py
    ${PROJECT_SOURCE_DIR}/*.md
    ${PROJECT_SOURCE_DIR}/pythonconverter_pkg/*.py
    ${PROJECT_SOURCE_DIR}/zeraconverterengines/*.py
    )

add_custom_target(${PROJECT_NAME} ALL
    SOURCES ${SOURCES}
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}

)

add_custom_command(TARGET ${PROJECT_NAME}
                   PRE_BUILD
                   COMMAND python setup.py sdist
                   WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    )

add_executable(${PROJECT_NAME}_exec IMPORTED [GLOBAL]
                IMPORTED_LOCATION ${PROJECT_SOURCE_DIR}
                )

install(CODE
    "
    execute_process(
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
        COMMAND python -m pip install dist/pythonconverter_pkg-0.0.1.tar.gz --prefix=${CMAKE_INSTALL_PREFIX})
    "
)

