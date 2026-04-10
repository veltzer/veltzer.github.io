#!/bin/bash -eu

# Manage Google API key restrictions for the calendar API key.
# Usage:
#   scripts/manage_api_key.sh show       - Show current key restrictions
#   scripts/manage_api_key.sh restrict   - Set HTTP referrer + API restrictions
#   scripts/manage_api_key.sh create     - Create a new API key with restrictions
#   scripts/manage_api_key.sh delete     - Delete the current API key from GCP and pass
#   scripts/manage_api_key.sh rotate     - Create new key, delete old key (rebuild & deploy in between)

PROJECT_ID="veltzer-calendar-id"
PASS_PATH="cloud/gcp/calendar"
ALLOWED_REFERRER="veltzer.github.io/*"

# Validate pass is available
if ! command -v pass &>/dev/null; then
    echo "ERROR: 'pass' (password-store) is not installed or not in PATH"
    exit 1
fi

# Read API key from pass
API_KEY=$(pass show "${PASS_PATH}" 2>/dev/null || true)

usage() {
    echo "Usage: $0 {show|restrict|create|delete|rotate}"
    echo "  show     - Show current API key details and restrictions"
    echo "  restrict - Restrict key to ${ALLOWED_REFERRER} and Calendar API only"
    echo "  create   - Create a new API key with restrictions applied"
    echo "  delete   - Delete the current API key from GCP and pass"
    echo "  rotate   - Create new key, delete old key (rebuild & deploy in between)"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

# Find the key's resource name by matching the key string
find_key_name() {
    local names
    names=$(gcloud services api-keys list \
        --project="${PROJECT_ID}" \
        --format="value(name)" 2>/dev/null)
    for name in ${names}; do
        local key
        key=$(gcloud services api-keys get-key-string "${name}" \
            --format="value(keyString)" 2>/dev/null || true)
        if [ "${key}" = "${API_KEY}" ]; then
            echo "${name}"
            return
        fi
    done
}

case "$1" in
    show)
        if [ -z "${API_KEY}" ]; then
            echo "ERROR: No API key found in pass at ${PASS_PATH}"
            exit 1
        fi
        echo "Looking up API key in project ${PROJECT_ID}..."
        KEY_NAME=$(find_key_name)
        if [ -z "${KEY_NAME}" ]; then
            echo "ERROR: Could not find key matching ${API_KEY} in project ${PROJECT_ID}"
            echo "Listing all keys:"
            gcloud services api-keys list --project="${PROJECT_ID}"
            exit 1
        fi
        echo "Key resource: ${KEY_NAME}"
        echo ""
        echo "=== Key Details ==="
        gcloud services api-keys describe "${KEY_NAME}" --project="${PROJECT_ID}"
        ;;

    restrict)
        if [ -z "${API_KEY}" ]; then
            echo "ERROR: No API key found in pass at ${PASS_PATH}"
            exit 1
        fi
        echo "Looking up API key in project ${PROJECT_ID}..."
        KEY_NAME=$(find_key_name)
        if [ -z "${KEY_NAME}" ]; then
            echo "ERROR: Could not find key matching ${API_KEY} in project ${PROJECT_ID}"
            exit 1
        fi
        echo "Key resource: ${KEY_NAME}"
        echo ""
        echo "Setting restrictions:"
        echo "  - HTTP referrer: ${ALLOWED_REFERRER}"
        echo "  - API: Google Calendar API"
        echo ""
        gcloud services api-keys update "${KEY_NAME}" \
            --project="${PROJECT_ID}" \
            --allowed-referrers="${ALLOWED_REFERRER}" \
            --api-target=service=calendar-json.googleapis.com
        echo ""
        echo "Done. Verifying:"
        gcloud services api-keys describe "${KEY_NAME}" --project="${PROJECT_ID}"
        ;;

    create)
        echo "Creating new API key in project ${PROJECT_ID}..."
        KEY_NAME=$(gcloud services api-keys create \
            --project="${PROJECT_ID}" \
            --display-name="calendar-api-key" \
            --allowed-referrers="${ALLOWED_REFERRER}" \
            --api-target=service=calendar-json.googleapis.com \
            --format="value(response.name)" 2>&1)
        echo "Created key resource: ${KEY_NAME}"
        echo ""
        echo "Fetching key string..."
        KEY_STRING=$(gcloud services api-keys get-key-string "${KEY_NAME}" \
            --project="${PROJECT_ID}" \
            --format="value(keyString)")
        echo ""
        echo "Storing key in pass at ${PASS_PATH}..."
        echo "${KEY_STRING}" | pass insert -e -f "${PASS_PATH}"
        echo ""
        echo "=== New API Key ==="
        echo "Key stored in pass at: ${PASS_PATH}"
        echo "Resource: ${KEY_NAME}"
        echo ""
        echo "Restrictions applied:"
        echo "  - HTTP referrer: ${ALLOWED_REFERRER}"
        echo "  - API: Google Calendar API"
        ;;

    delete)
        if [ -z "${API_KEY}" ]; then
            echo "ERROR: No API key found in pass at ${PASS_PATH}"
            exit 1
        fi
        echo "Looking up API key in project ${PROJECT_ID}..."
        KEY_NAME=$(find_key_name)
        if [ -z "${KEY_NAME}" ]; then
            echo "ERROR: Could not find key matching stored key in project ${PROJECT_ID}"
            exit 1
        fi
        echo "Key resource: ${KEY_NAME}"
        echo ""
        echo "Deleting API key from GCP..."
        gcloud services api-keys delete "${KEY_NAME}" --project="${PROJECT_ID}"
        echo ""
        echo "Removing key from pass..."
        pass rm -f "${PASS_PATH}"
        echo ""
        echo "Done. API key deleted from GCP and pass."
        ;;

    rotate)
        # Save old key info for deletion later
        OLD_API_KEY="${API_KEY}"
        if [ -z "${OLD_API_KEY}" ]; then
            echo "No existing key found in pass. Running create instead."
            exec "$0" create
        fi
        OLD_KEY_NAME=$(find_key_name)
        if [ -z "${OLD_KEY_NAME}" ]; then
            echo "WARNING: Could not find old key in GCP (may already be deleted)"
        fi

        # Create new key
        echo "=== Creating new API key ==="
        KEY_NAME=$(gcloud services api-keys create \
            --project="${PROJECT_ID}" \
            --display-name="calendar-api-key" \
            --allowed-referrers="${ALLOWED_REFERRER}" \
            --api-target=service=calendar-json.googleapis.com \
            --format="value(response.name)" 2>&1)
        echo "Created key resource: ${KEY_NAME}"
        KEY_STRING=$(gcloud services api-keys get-key-string "${KEY_NAME}" \
            --project="${PROJECT_ID}" \
            --format="value(keyString)")
        echo "${KEY_STRING}" | pass insert -e -f "${PASS_PATH}"
        echo "New key stored in pass at ${PASS_PATH}"
        echo ""
        echo ">>> Rebuild and deploy the site now, then press Enter to delete the old key <<<"
        read -r
        echo ""

        # Delete old key
        if [ -n "${OLD_KEY_NAME}" ]; then
            echo "=== Deleting old API key ==="
            gcloud services api-keys delete "${OLD_KEY_NAME}" --project="${PROJECT_ID}"
            echo "Old key deleted."
        fi
        echo ""
        echo "Done. Key rotation complete."
        ;;

    *)
        usage
        ;;
esac
