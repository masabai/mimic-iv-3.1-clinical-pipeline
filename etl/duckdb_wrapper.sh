#!/bin/bash
# Wraps every duckdb call from build_mimic.sh to inject memory settings.
# Prepends init SQL to any -f or -c invocation.
#INIT="SET memory_limit='3GB'; SET threads=2; SET max_temp_directory_size='60GB'; SET temp_directory='/duckdb/duckdb_temp'; SET preserve_insertion_order=false;"
INIT="SET memory_limit='6GB'; SET threads=4; SET max_temp_directory_size='60GB'; SET temp_directory='/duckdb/duckdb_temp'; SET preserve_insertion_order=false;"
#INIT="SET memory_limit='3GB'; SET threads=2; SET max_temp_directory_size='60GB'; SET temp_directory='/duckdb/duckdb_temp'; SET preserve_insertion_order=false;"
ARGS=()
i=1
while [ $i -le $# ]; do
    arg="${!i}"
    if [ "$arg" = "-c" ]; then
        i=$((i+1))
        ARGS+=("-c" "${INIT} ${!i}")
    elif [ "$arg" = "-f" ]; then
        i=$((i+1))
        TMPF=$(mktemp /tmp/duckdb_init_XXXXXX.sql)
        echo "$INIT" > "$TMPF"
        cat "${!i}" >> "$TMPF"
        ARGS+=("-f" "$TMPF")
    else
        ARGS+=("$arg")
    fi
    i=$((i+1))
done

exec /usr/local/bin/duckdb.real "${ARGS[@]}"
