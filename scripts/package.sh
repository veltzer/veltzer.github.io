#!/bin/bash -eu

# A script to create an isolated project, install npm packages from a file,
# and bundle them using Vite into specified output files.

# --- Default Configuration ---
JS_FILENAME=""
CSS_FILENAME=""
VERBOSE=false
KEEP_DIR=false

# --- Function to display usage information ---
usage() {
    echo "Usage: $0 [-v] [-k] [-j /path/to/app.js] [-c /path/to/style.css] <path/to/packages.txt>"
    echo "  -v    Enable verbose output (the script is quiet by default)."
    echo "  -k    Keep the temporary build directory for debugging."
    echo "  -j    Set the output path and name for the bundled JavaScript file."
    echo "  -c    Set the output path and name for the bundled CSS file."
    exit 1
}

# --- Logging function for verbose mode ---
log_verbose() {
    if [ "$VERBOSE" = true ]; then
        # Use -e to interpret backslash escapes like \n
        echo -e "$1"
    fi
}

# --- Parse Command-Line Options ---
while getopts ":vkj:c:" opt; do
  case ${opt} in
    v )
      VERBOSE=true
      ;;
    k )
      KEEP_DIR=true
      ;;
    j )
      JS_FILENAME=$OPTARG
      ;;
    c )
      CSS_FILENAME=$OPTARG
      ;;
    \? )
      echo "Invalid Option: -$OPTARG" 1>&2
      usage
      ;;
    : )
      echo "Invalid Option: -$OPTARG requires an argument" 1>&2
      usage
      ;;
  esac
done
shift $((OPTIND -1))

# --- Set up redirection based on verbosity ---
REDIRECT_CMD="> /dev/null 2>&1"
if [ "$VERBOSE" = true ]; then
    REDIRECT_CMD=""
fi

# --- Check for Input ---
# Ensure exactly one argument (the file path) remains after parsing options.
if [ "$#" -ne 1 ]; then
    usage
fi

PACKAGE_FILE="$1"

# Check if the file exists and is readable.
if [ ! -f "$PACKAGE_FILE" ]; then
    echo "Error: File not found at '$PACKAGE_FILE'"
    exit 1
fi

# Read packages from the file into a variable.
# xargs is used to trim whitespace and handle empty lines gracefully.
PACKAGES=$(cat "$PACKAGE_FILE" | xargs)

if [ -z "$PACKAGES" ]; then
    echo "Error: No packages found in '$PACKAGE_FILE'."
    exit 1
fi

# --- Main Execution ---
# Create a temporary directory to work in.
TMP_PARENT_DIR=$(mktemp -d -t vite-bundler-parent-XXXXXX)
PROJECT_SUBDIR="vite-project" # A fixed name for the subdirectory Vite will create
PROJECT_DIR="$TMP_PARENT_DIR/$PROJECT_SUBDIR"

log_verbose "-----------------------------------------------------"
log_verbose "Creating isolated project in: $PROJECT_DIR"
log_verbose "Packages to install from '$PACKAGE_FILE': $PACKAGES"
log_verbose "-----------------------------------------------------"

# Navigate into the temporary parent directory.
cd "$TMP_PARENT_DIR" || exit

# Step 1: Initialize a Vite project non-interactively in a subdirectory.
log_verbose "\n[1/7] Initializing a new Vite project..."
# This creates a new directory named $PROJECT_SUBDIR
eval "npm create vite@latest $PROJECT_SUBDIR -- --template vanilla $REDIRECT_CMD"
if [ $? -ne 0 ]; then
    echo "Error: Failed to initialize Vite project."
    rm -rf "$TMP_PARENT_DIR"
    exit 1
fi

# Navigate into the newly created project directory
cd "$PROJECT_DIR" || exit

# Step 2: Install the packages read from the file.
log_verbose "\n[2/7] Installing specified npm packages..."
eval "npm install $PACKAGES $REDIRECT_CMD"
if [ $? -ne 0 ]; then
    echo "Error: Failed to install npm packages."
    rm -rf "$TMP_PARENT_DIR"
    exit 1
fi

# Step 3: Create a main.js file that imports all the packages.
log_verbose "\n[3/7] Generating main.js to include all packages..."
# Overwrite the default src/main.js created by the Vite template
> src/main.js
echo "console.log('All packages imported.');" >> src/main.js
# Loop through the packages, stripping version numbers for the import statement.
for pkg_with_version in $PACKAGES; do
    # This handles both unscoped (react) and scoped (@angular/core) packages with versions.
    if [[ $pkg_with_version == @* ]]; then
        # Scoped package: @scope/name@version or @scope/name
        at_count=$(grep -o "@" <<< "$pkg_with_version" | wc -l)
        if [ $at_count -gt 1 ]; then
            # Has a version, like @scope/name@1.2.3. Get everything before the last '@'.
            pkg_name=$(rev <<< "$pkg_with_version" | cut -d@ -f2- | rev)
        else
            # No version, like @scope/name
            pkg_name=$pkg_with_version
        fi
    else
        # Unscoped package: name@version or name
        pkg_name=$(echo "$pkg_with_version" | cut -d@ -f1)
    fi
    # Import the main package JavaScript
    echo "import '$pkg_name';" >> src/main.js
    
    # **ROBUST FIX**: Read package.json to find the correct CSS file.
    CSS_IMPORT_PATH=""
    PKG_JSON_PATH="node_modules/$pkg_name/package.json"

    if [ -f "$PKG_JSON_PATH" ]; then
        # Use grep and sed to parse the "style" field from package.json. This is more reliable.
        STYLE_FIELD_VALUE=$(grep '"style":' "$PKG_JSON_PATH" | sed -n 's/.*"style": *"\([^"]*\)".*/\1/p')
        if [ -n "$STYLE_FIELD_VALUE" ]; then
            CSS_IMPORT_PATH="$pkg_name/$STYLE_FIELD_VALUE"
        fi
    fi
    
    # Fallback to the old find method if the "style" field isn't in package.json
    if [ -z "$CSS_IMPORT_PATH" ]; then
        CSS_FILE_IN_DIST=$(find "node_modules/$pkg_name/dist" -name "*.css" 2>/dev/null | head -n 1)
        if [ -n "$CSS_FILE_IN_DIST" ]; then
            CSS_IMPORT_PATH=${CSS_FILE_IN_DIST#node_modules/}
        fi
    fi

    if [ -n "$CSS_IMPORT_PATH" ]; then
        log_verbose "Found CSS for '$pkg_name', adding to bundle: import '$CSS_IMPORT_PATH';"
        echo "import '$CSS_IMPORT_PATH';" >> src/main.js
    fi
done
log_verbose "Successfully created main.js."

# Step 4: Generate Vite config file to control output filenames.
log_verbose "\n[4/7] Generating Vite configuration..."
# If a filename is provided, use it. Otherwise, let Vite use its default [name]-[hash] pattern.
JS_OUT=${JS_FILENAME:-"assets/bundle-[hash].js"}
CSS_OUT=${CSS_FILENAME:-"assets/style-[hash].css"}

# Use a heredoc to create the vite.config.js file.
cat > vite.config.js << EOL
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        entryFileNames: \`$JS_OUT\`,
        assetFileNames: (assetInfo) => {
          if (assetInfo.name.endsWith('.css')) {
            return \`$CSS_OUT\`;
          }
          return 'assets/[name]-[hash][extname]';
        }
      }
    }
  }
});
EOL
log_verbose "Successfully created vite.config.js."

# Step 5: Run the Vite build process.
log_verbose "\n[5/7] Building the project with Vite..."
eval "npm run build $REDIRECT_CMD"
if [ $? -ne 0 ]; then
    echo "Error: Vite build failed."
    rm -rf "$TMP_PARENT_DIR"
    exit 1
fi

# Step 6: Move final assets to their destination.
log_verbose "\n[6/7] Moving build artifacts to final destination..."
# Find the generated JS and CSS files in the temporary dist directory.
JS_BUNDLE_IN_DIST=$(find dist -name "*.js")
CSS_BUNDLE_IN_DIST=$(find dist -name "*.css")

# Move the JavaScript file
if [ -f "$JS_BUNDLE_IN_DIST" ]; then
    DEST_JS_PATH=${JS_FILENAME:-$(basename "$JS_BUNDLE_IN_DIST")}
    mkdir -p "$(dirname "$DEST_JS_PATH")"
    mv "$JS_BUNDLE_IN_DIST" "$DEST_JS_PATH"
    echo "JavaScript bundle created at: $DEST_JS_PATH"
else
    log_verbose "Warning: No JavaScript bundle was created."
fi

# Move the CSS file
if [ -f "$CSS_BUNDLE_IN_DIST" ]; then
    DEST_CSS_PATH=${CSS_FILENAME:-$(basename "$CSS_BUNDLE_IN_DIST")}
    mkdir -p "$(dirname "$DEST_CSS_PATH")"
    mv "$CSS_BUNDLE_IN_DIST" "$DEST_CSS_PATH"
    echo "CSS bundle created at: $DEST_CSS_PATH"
else
    log_verbose "Info: No CSS bundle was created."
fi

# Step 7: Clean up the temporary project directory unless told not to.
if [ "$KEEP_DIR" = false ]; then
    log_verbose "\n[7/7] Cleaning up temporary project directory..."
    rm -rf "$TMP_PARENT_DIR"
else
    log_verbose "\n[7/7] Temporary build directory kept at: $TMP_PARENT_DIR"
fi

log_verbose "\nSuccess! The bundled files have been created."
