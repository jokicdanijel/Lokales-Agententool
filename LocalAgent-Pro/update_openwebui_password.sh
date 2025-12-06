#!/usr/bin/env bash
# OpenWebUI Password Update Utility
# Updates password in OpenWebUI SQLite database using Docker

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Default values
DOCKER_VOLUME="openwebui_openwebui_data"
DB_PATH="/data/webui.db"
SQLITE_IMAGE="nouchka/sqlite3"

# Function to display usage
usage() {
    echo -e "${BOLD}OpenWebUI Password Update Utility${NC}"
    echo ""
    echo "Usage: $0 -e EMAIL -p PASSWORD_HASH [-v VOLUME_NAME]"
    echo ""
    echo "Options:"
    echo "  -e EMAIL          Email address of the user to update"
    echo "  -p PASSWORD_HASH  Bcrypt password hash (e.g., \$2b\$...)"
    echo "  -v VOLUME_NAME    Docker volume name (default: openwebui_openwebui_data)"
    echo "  -h                Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 -e user@example.com -p '\$2b\$12\$abc123...'"
    echo ""
    echo "Note: The password hash must be a valid bcrypt hash."
    echo "      You can generate one using Python's bcrypt library or online tools."
    exit 1
}

# Parse command line arguments
EMAIL=""
PASSWORD_HASH=""

while getopts "e:p:v:h" opt; do
    case $opt in
        e)
            EMAIL="$OPTARG"
            ;;
        p)
            PASSWORD_HASH="$OPTARG"
            ;;
        v)
            DOCKER_VOLUME="$OPTARG"
            ;;
        h)
            usage
            ;;
        \?)
            echo -e "${RED}Invalid option: -$OPTARG${NC}" >&2
            usage
            ;;
    esac
done

# Validate required parameters
if [ -z "$EMAIL" ] || [ -z "$PASSWORD_HASH" ]; then
    echo -e "${RED}Error: Email and password hash are required${NC}" >&2
    usage
fi

# Validate email format
if ! echo "$EMAIL" | grep -qE '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'; then
    echo -e "${RED}Error: Invalid email format${NC}" >&2
    exit 1
fi

# Validate password hash format (bcrypt format: $2a$, $2b$, or $2y$ followed by rounds and hash)
# Bcrypt hashes are always 60 characters long
if ! echo "$PASSWORD_HASH" | grep -qE '^\$2[aby]\$[0-9]{2}\$.{53}$'; then
    echo -e "${RED}Error: Invalid bcrypt password hash format${NC}" >&2
    echo -e "${YELLOW}Expected format: \$2b\$12\$... (60 characters total)${NC}" >&2
    echo -e "${YELLOW}Actual length: $(echo -n "$PASSWORD_HASH" | wc -c) characters${NC}" >&2
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not in PATH${NC}" >&2
    exit 1
fi

# Check if sg command is available (for docker group access)
if ! command -v sg &> /dev/null; then
    echo -e "${YELLOW}Note: 'sg' command not found, using 'docker' directly${NC}"
    echo -e "${YELLOW}      If you get permission errors, try adding your user to the docker group${NC}"
fi

# Check if Docker volume exists
if ! docker volume inspect "$DOCKER_VOLUME" &> /dev/null; then
    echo -e "${RED}Error: Docker volume '$DOCKER_VOLUME' does not exist${NC}" >&2
    echo -e "${YELLOW}Available volumes:${NC}"
    docker volume ls | grep -i webui || echo "  (no volumes matching 'webui' found)"
    exit 1
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  OpenWebUI Password Update${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "  Volume:    ${DOCKER_VOLUME}"
echo -e "  Database:  ${DB_PATH}"
echo -e "  Email:     ${EMAIL}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo ""

# Construct the SQL command
# Note: Input validation above ensures EMAIL and PASSWORD_HASH contain only valid characters
# to prevent SQL injection. Email is validated against RFC format, and password hash
# is validated against bcrypt format ($2a$/$2b$/$2y$ + rounds + 53 char hash)
SQL_CMD="UPDATE auth SET password='${PASSWORD_HASH}' WHERE email='${EMAIL}';"

echo -e "${YELLOW}⚠️  Warning: This will update the password in the database${NC}"
echo -e "${YELLOW}   Make sure you have a backup before proceeding!${NC}"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Operation cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Updating password...${NC}"

# Execute the SQL command using Docker
# Build the docker command based on whether sg is available
if command -v sg &> /dev/null; then
    # Use sg docker for group access
    # Note: Variables are validated above - DOCKER_VOLUME exists, EMAIL and PASSWORD_HASH are validated
    if sg docker -c "docker run --rm -v '${DOCKER_VOLUME}:/data' '${SQLITE_IMAGE}' '${DB_PATH}' \"${SQL_CMD}\"" 2>&1; then
        UPDATE_SUCCESS=true
    else
        UPDATE_SUCCESS=false
    fi
else
    # Use docker directly
    if docker run --rm -v "${DOCKER_VOLUME}:/data" "${SQLITE_IMAGE}" "${DB_PATH}" "${SQL_CMD}" 2>&1; then
        UPDATE_SUCCESS=true
    else
        UPDATE_SUCCESS=false
    fi
fi

if [ "$UPDATE_SUCCESS" = true ]; then
    echo ""
    echo -e "${GREEN}✅ Password updated successfully${NC}"
    
    # Verify the update
    echo ""
    echo -e "${BLUE}Verifying update...${NC}"
    # Email already validated above, safe to use in SQL query
    VERIFY_CMD="SELECT email, password FROM auth WHERE email='${EMAIL}';"
    
    # Verify using the same method
    if command -v sg &> /dev/null; then
        VERIFY_OUTPUT=$(sg docker -c "docker run --rm -v '${DOCKER_VOLUME}:/data' '${SQLITE_IMAGE}' '${DB_PATH}' \"${VERIFY_CMD}\"" 2>&1)
    else
        VERIFY_OUTPUT=$(docker run --rm -v "${DOCKER_VOLUME}:/data" "${SQLITE_IMAGE}" "${DB_PATH}" "${VERIFY_CMD}" 2>&1)
    fi
    
    if echo "$VERIFY_OUTPUT" | grep -q "$EMAIL"; then
        echo -e "${GREEN}✅ Verification successful${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not verify the update${NC}"
    fi
else
    echo ""
    echo -e "${RED}❌ Failed to update password${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  Password Update Complete${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "You can now log in to OpenWebUI with the new password."
echo ""
