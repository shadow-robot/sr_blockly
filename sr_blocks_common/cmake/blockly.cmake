set(BLOCKS_UNCOMPRESSED_JS_FILE "blocks_uncompressed.js" CACHE STRING "Name of the blockly javascript file")

function(generate_blockly_js)

  set(TEMP_BLOCKS_UNCOMPRESSED_JS_FILE "blocks_uncompressed.js.in")

  file(GLOB_RECURSE PACKAGE_JS_FILES *.js)
  file(WRITE ${TEMP_BLOCKS_UNCOMPRESSED_JS_FILE}  "")

  foreach(PACKAGE_JS_FILE ${PACKAGE_JS_FILES})
    if(NOT (${PACKAGE_JS_FILE} MATCHES "${BLOCKS_UNCOMPRESSED_JS_FILE}$"))
      stamp(${PACKAGE_JS_FILE})
      cat(${PACKAGE_JS_FILE} ${TEMP_BLOCKS_UNCOMPRESSED_JS_FILE})
    endif()
  endforeach()

  configure_file(${TEMP_BLOCKS_UNCOMPRESSED_JS_FILE} ${CMAKE_CURRENT_SOURCE_DIR}/${BLOCKS_UNCOMPRESSED_JS_FILE} COPYONLY)

endfunction()
