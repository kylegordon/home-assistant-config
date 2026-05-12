#!/bin/bash

# Script to compile (and optionally upload) all ESPHome files that use tx-ultimate-easy
# Usage: ./compile_tx_ultimate.sh [--upload]

ESPHOME_VERSION="2026.1.1"
UPLOAD_MODE=false

# Parse arguments
if [[ "$1" == "--upload" ]]; then
    UPLOAD_MODE=true
    echo "Upload mode enabled"
fi

# Find all YAML files that include tx_ultimate_easy_common.yaml
echo "Searching for ESPHome files that use tx-ultimate-easy..."
FILES=$(grep -l "tx_ultimate_easy_common" esphome/*.yaml 2>/dev/null || true)

if [[ -z "$FILES" ]]; then
    echo "No ESPHome files found that use tx-ultimate-easy"
    exit 0
fi

# Convert to array
mapfile -t FILE_ARRAY <<< "$FILES"

# Arrays to track results
declare -A COMPILE_RESULTS
declare -A UPLOAD_RESULTS

echo "Found ${#FILE_ARRAY[@]} file(s) to process:"
for file in "${FILE_ARRAY[@]}"; do
    echo "  - $file"
done
echo ""

# Process each file
for file in "${FILE_ARRAY[@]}"; do
    echo "========================================"
    echo "Processing: $file"
    echo "========================================"
    
    # Compile
    echo "Compiling $file..."
    if docker run --rm -v "${PWD}":/config esphome/esphome:${ESPHOME_VERSION} compile "$file"; then
        COMPILE_RESULTS["$file"]=0
        echo "✓ Compilation successful for $file"
    else
        COMPILE_RESULTS["$file"]=$?
        echo "ERROR: Compilation failed for $file"
    fi
    echo ""
    
    # Upload if requested
    if [[ "$UPLOAD_MODE" == true ]]; then
        echo "Uploading $file..."
        docker run --rm --privileged --net host -v "${PWD}":/config esphome/esphome:${ESPHOME_VERSION} upload "$file"
        rc=$?
        UPLOAD_RESULTS["$file"]=$rc
        if [[ $rc -eq 0 ]]; then
            echo "✓ Upload successful for $file"
        else
            echo "ERROR: Upload failed for $file (exit code: $rc)"
        fi
        echo ""
    fi
done

echo "========================================"
echo "SUMMARY"
echo "========================================"
echo ""
echo "Compilation Results:"
echo "--------------------"
for file in "${FILE_ARRAY[@]}"; do
    exit_code="${COMPILE_RESULTS[$file]}"
    if [[ "$exit_code" == "0" ]]; then
        status="✓ SUCCESS"
    else
        status="✗ FAILED (exit code: $exit_code)"
    fi
    printf "%-50s %s\n" "$file" "$status"
done

if [[ "$UPLOAD_MODE" == true ]]; then
    echo ""
    echo "Upload Results:"
    echo "---------------"
    for file in "${FILE_ARRAY[@]}"; do
        exit_code="${UPLOAD_RESULTS[$file]}"
        if [[ "$exit_code" == "0" ]]; then
            status="✓ SUCCESS"
        else
            status="✗ FAILED (exit code: $exit_code)"
        fi
        printf "%-50s %s\n" "$file" "$status"
    done
fi

echo ""
echo "========================================"
echo "Processing complete!"
echo "========================================"

# Check if any compilations or uploads failed
HAS_FAILURES=false
for file in "${FILE_ARRAY[@]}"; do
    if [[ "${COMPILE_RESULTS[$file]}" != "0" ]]; then
        HAS_FAILURES=true
        break
    fi
    if [[ "$UPLOAD_MODE" == true ]] && [[ "${UPLOAD_RESULTS[$file]}" != "0" ]]; then
        HAS_FAILURES=true
        break
    fi
done

if [[ "$HAS_FAILURES" == true ]]; then
    echo "⚠ Some operations failed. See summary above."
    exit 1
else
    echo "✓ All operations completed successfully!"
    exit 0
fi
