#!/bin/bash

# This file is sourced by univention postinst scripts,
# ensure that the PATH contains our local overrides.
local_bin=/usr/local/bin
if ! echo "$PATH" | grep -E -q "(^|:)$local_bin($|:)"; then
  PATH=$local_bin:$PATH
fi

# [EOF]
