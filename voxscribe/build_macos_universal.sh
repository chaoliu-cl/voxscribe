#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="VoxScribe"
DEFAULT_BUNDLE_ID="io.github.chaoliu-cl.voxscribe"
HOST_ARCH="$(uname -m)"

PYTHON_BIN="${PYTHON_BIN:-python3}"
ARM64_PYTHON=""
X86_64_PYTHON=""
BUNDLE_ID="$DEFAULT_BUNDLE_ID"
CODESIGN_IDENTITY=""
INSTALLER_SIGN_IDENTITY=""
ENTITLEMENTS_FILE=""
ARM64_APP_INPUT=""
X86_64_APP_INPUT=""
KEEP_VENVS=0
SKIP_CLEAN=0

BUILD_ROOT="$SCRIPT_DIR/build/macos"
DIST_ROOT="$SCRIPT_DIR/dist"
DIST_APPS_ROOT="$DIST_ROOT/macos"
PKG_ROOT="$BUILD_ROOT/pkg"
SPEC_PATH="$SCRIPT_DIR/voxscribe-macos.spec"
ICON_PATH="$BUILD_ROOT/${APP_NAME}.icns"
DIST_XML_PATH="$BUILD_ROOT/distribution.xml"
FINAL_PKG_PATH=""

usage() {
    cat <<EOF
Build a macOS universal installer for ${APP_NAME}.

This workflow creates one native Apple Silicon app bundle and one native Intel
app bundle, then wraps both in a single .pkg installer that auto-selects the
correct payload at install time.

Usage:
  ./build_macos_universal.sh [options]

Options:
  --python PATH                    Universal2 Python to use for both builds.
  --arm64-python PATH              Python to use for the Apple Silicon build.
  --x86_64-python PATH             Python to use for the Intel build.
  --bundle-id ID                   macOS bundle identifier.
  --codesign-identity NAME         Developer ID Application identity for app signing.
  --installer-sign-identity NAME   Developer ID Installer identity for pkg signing.
  --entitlements-file PATH         Optional entitlements plist for app signing.
  --arm64-app PATH                 Reuse a prebuilt Apple Silicon app bundle.
  --x86_64-app PATH                Reuse a prebuilt Intel app bundle.
  --keep-venvs                     Reuse build virtualenvs between runs.
  --skip-clean                     Keep previous dist/build artifacts when possible.
  -h, --help                       Show this help text.

Notes:
  - Building both architectures locally is intended for Apple Silicon hosts.
  - Intel builds on Apple Silicon require Rosetta 2.
  - If you already have one architecture's .app bundle, pass it with
    --arm64-app or --x86_64-app and the script will package it directly.
EOF
}

log() {
    printf '[voxscribe-macos] %s\n' "$*"
}

die() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

make_absolute() {
    local path_value="$1"

    if [[ "$path_value" = /* ]]; then
        printf '%s\n' "$path_value"
    else
        printf '%s\n' "$(cd "$(dirname "$path_value")" && pwd)/$(basename "$path_value")"
    fi
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

run_python_for_arch() {
    local target_arch="$1"
    local python_bin="$2"
    shift 2

    case "$target_arch" in
        arm64)
            /usr/bin/arch -arm64 "$python_bin" "$@"
            ;;
        x86_64)
            /usr/bin/arch -x86_64 "$python_bin" "$@"
            ;;
        *)
            "$python_bin" "$@"
            ;;
    esac
}

verify_python_arch() {
    local target_arch="$1"
    local python_bin="$2"
    local actual_arch

    actual_arch="$(run_python_for_arch "$target_arch" "$python_bin" -c 'import platform; print(platform.machine())')"
    if [[ "$actual_arch" != "$target_arch" ]]; then
        die "Python at $python_bin did not start as $target_arch (reported $actual_arch)"
    fi
}

read_app_version() {
    local version

    version="$(sed -n 's/^__version__ = "\(.*\)"$/\1/p' "$SCRIPT_DIR/__init__.py" | head -n 1)"
    [[ -n "$version" ]] || die "Unable to determine application version from $SCRIPT_DIR/__init__.py"
    printf '%s\n' "$version"
}

prepare_icon() {
    local source_icon=""
    local iconset_dir="$BUILD_ROOT/icon.iconset"
    local source_png="$BUILD_ROOT/icon-source.png"
    local size
    local retina_size

    if [[ -f "$SCRIPT_DIR/assets/app.icns" ]]; then
        cp "$SCRIPT_DIR/assets/app.icns" "$ICON_PATH"
        return
    fi

    if [[ -f "$SCRIPT_DIR/assets/app.ico" ]]; then
        source_icon="$SCRIPT_DIR/assets/app.ico"
    elif [[ -f "$SCRIPT_DIR/assets/splash.png" ]]; then
        source_icon="$SCRIPT_DIR/assets/splash.png"
    else
        die "No icon source found. Add assets/app.icns, assets/app.ico, or assets/splash.png."
    fi

    rm -rf "$iconset_dir" "$source_png" "$ICON_PATH"
    mkdir -p "$iconset_dir"

    sips -s format png "$source_icon" --out "$source_png" >/dev/null

    for size in 16 32 128 256 512; do
        retina_size=$((size * 2))
        sips -z "$size" "$size" "$source_png" --out "$iconset_dir/icon_${size}x${size}.png" >/dev/null
        sips -z "$retina_size" "$retina_size" "$source_png" \
            --out "$iconset_dir/icon_${size}x${size}@2x.png" >/dev/null
    done

    iconutil -c icns "$iconset_dir" -o "$ICON_PATH"
}

ensure_rosetta() {
    if ! /usr/bin/arch -x86_64 /usr/bin/true >/dev/null 2>&1; then
        die "Rosetta 2 is required for the x86_64 build on Apple Silicon. Install it with: softwareupdate --install-rosetta"
    fi
}

prepare_arch_environment() {
    local target_arch="$1"
    local python_bin="$2"
    local venv_dir="$3"

    verify_python_arch "$target_arch" "$python_bin"

    if [[ ! -d "$venv_dir" ]]; then
        log "Creating $target_arch virtualenv at $venv_dir"
        run_python_for_arch "$target_arch" "$python_bin" -m venv "$venv_dir"
    fi

    log "Refreshing build dependencies in the $target_arch environment"
    run_python_for_arch "$target_arch" "$venv_dir/bin/python" -m pip install --upgrade pip setuptools wheel
    run_python_for_arch "$target_arch" "$venv_dir/bin/python" -m pip install -r "$SCRIPT_DIR/requirements-build.txt"
}

verify_app_bundle_arch() {
    local app_path="$1"
    local expected_arch="$2"
    local executable="$app_path/Contents/MacOS/$APP_NAME"
    local archs
    local bad_extensions=()
    local extension
    local extension_archs

    [[ -f "$executable" ]] || die "App executable not found: $executable"

    archs="$(lipo -archs "$executable")"
    if [[ "$archs" != *"$expected_arch"* ]]; then
        die "Expected $executable to contain the $expected_arch slice, found: $archs"
    fi

    while IFS= read -r -d '' extension; do
        extension_archs="$(lipo -archs "$extension" 2>/dev/null || true)"
        if [[ -z "$extension_archs" || "$extension_archs" != *"$expected_arch"* ]]; then
            bad_extensions+=("$extension")
        fi
    done < <(find "$app_path" -type f -name '*.so' -print0)

    if ((${#bad_extensions[@]} > 0)); then
        printf 'Error: Some extension modules in %s are missing the %s slice:\n' "$app_path" "$expected_arch" >&2
        printf '  %s\n' "${bad_extensions[@]}" >&2
        exit 1
    fi
}

build_app_for_arch() {
    local target_arch="$1"
    local python_bin="$2"
    local venv_dir="$3"
    local dist_dir="$DIST_APPS_ROOT/$target_arch"
    local work_dir="$BUILD_ROOT/pyinstaller-$target_arch"
    local app_path

    prepare_arch_environment "$target_arch" "$python_bin" "$venv_dir"

    rm -rf "$dist_dir" "$work_dir"
    mkdir -p "$dist_dir" "$work_dir"

    log "Building ${APP_NAME}.app for $target_arch"
    VOXSCRIBE_APP_NAME="$APP_NAME" \
    VOXSCRIBE_APP_VERSION="$APP_VERSION" \
    VOXSCRIBE_BUNDLE_ID="$BUNDLE_ID" \
    VOXSCRIBE_MAC_ICON="$ICON_PATH" \
    VOXSCRIBE_TARGET_ARCH="$target_arch" \
    VOXSCRIBE_CODESIGN_IDENTITY="$CODESIGN_IDENTITY" \
    VOXSCRIBE_ENTITLEMENTS_FILE="$ENTITLEMENTS_FILE" \
    run_python_for_arch "$target_arch" "$venv_dir/bin/python" -m PyInstaller \
        --noconfirm \
        --clean \
        --distpath "$dist_dir" \
        --workpath "$work_dir" \
        "$SPEC_PATH"

    app_path="$dist_dir/${APP_NAME}.app"
    [[ -d "$app_path" ]] || die "Expected app bundle was not created: $app_path"
    verify_app_bundle_arch "$app_path" "$target_arch"
    printf '%s\n' "$app_path"
}

package_app_bundle() {
    local app_path="$1"
    local target_arch="$2"
    local component_pkg="$PKG_ROOT/${APP_NAME}-${target_arch}.pkg"
    local component_id="${BUNDLE_ID}.${target_arch}"

    rm -f "$component_pkg"

    pkgbuild \
        --component "$app_path" \
        --identifier "$component_id" \
        --version "$APP_VERSION" \
        --install-location /Applications \
        "$component_pkg" >/dev/null

    printf '%s\n' "$component_pkg"
}

write_distribution_xml() {
    local arm_pkg_name="$1"
    local x86_pkg_name="$2"
    local arm_pkg_id="${BUNDLE_ID}.arm64"
    local x86_pkg_id="${BUNDLE_ID}.x86_64"

    cat >"$DIST_XML_PATH" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="1">
    <title>${APP_NAME}</title>
    <pkg-ref id="${arm_pkg_id}"/>
    <pkg-ref id="${x86_pkg_id}"/>
    <options customize="never" require-scripts="false" hostArchitectures="x86_64,arm64"/>
    <domains enable_anywhere="false" enable_currentUserHome="false" enable_localSystem="true"/>
    <choices-outline>
        <line choice="default">
            <line choice="${arm_pkg_id}"/>
            <line choice="${x86_pkg_id}"/>
        </line>
    </choices-outline>
    <choice id="default"/>
    <choice
        id="${arm_pkg_id}"
        title="${APP_NAME} (Apple Silicon)"
        description="Install the native Apple Silicon build."
        visible="false"
        selected="system.sysctl('hw.optional.arm64') == '1'">
        <pkg-ref id="${arm_pkg_id}"/>
    </choice>
    <pkg-ref id="${arm_pkg_id}" version="${APP_VERSION}" onConclusion="none">${arm_pkg_name}</pkg-ref>
    <choice
        id="${x86_pkg_id}"
        title="${APP_NAME} (Intel)"
        description="Install the native Intel build."
        visible="false"
        selected="system.sysctl('hw.optional.arm64') != '1'">
        <pkg-ref id="${x86_pkg_id}"/>
    </choice>
    <pkg-ref id="${x86_pkg_id}" version="${APP_VERSION}" onConclusion="none">${x86_pkg_name}</pkg-ref>
</installer-gui-script>
EOF
}

build_installer_product() {
    local output_path="$1"
    local product_id="${BUNDLE_ID}.installer"

    rm -f "$output_path"

    if [[ -n "$INSTALLER_SIGN_IDENTITY" ]]; then
        productbuild \
            --distribution "$DIST_XML_PATH" \
            --package-path "$PKG_ROOT" \
            --identifier "$product_id" \
            --version "$APP_VERSION" \
            --sign "$INSTALLER_SIGN_IDENTITY" \
            "$output_path" >/dev/null
    else
        productbuild \
            --distribution "$DIST_XML_PATH" \
            --package-path "$PKG_ROOT" \
            --identifier "$product_id" \
            --version "$APP_VERSION" \
            "$output_path" >/dev/null
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --python)
            [[ $# -ge 2 ]] || die "Missing value for $1"
            PYTHON_BIN="$2"
            shift 2
            ;;
        --arm64-python)
            [[ $# -ge 2 ]] || die "Missing value for $1"
            ARM64_PYTHON="$2"
            shift 2
            ;;
        --x86_64-python)
            [[ $# -ge 2 ]] || die "Missing value for $1"
            X86_64_PYTHON="$2"
            shift 2
            ;;
        --bundle-id)
            [[ $# -ge 2 ]] || die "Missing value for $1"
            BUNDLE_ID="$2"
            shift 2
            ;;
        --codesign-identity)
            [[ $# -ge 2 ]] || die "Missing value for $1"
            CODESIGN_IDENTITY="$2"
            shift 2
            ;;
        --installer-sign-identity)
            [[ $# -ge 2 ]] || die "Missing value for $1"
            INSTALLER_SIGN_IDENTITY="$2"
            shift 2
            ;;
        --entitlements-file)
            [[ $# -ge 2 ]] || die "Missing value for $1"
            ENTITLEMENTS_FILE="$(make_absolute "$2")"
            shift 2
            ;;
        --arm64-app)
            [[ $# -ge 2 ]] || die "Missing value for $1"
            ARM64_APP_INPUT="$(make_absolute "$2")"
            shift 2
            ;;
        --x86_64-app)
            [[ $# -ge 2 ]] || die "Missing value for $1"
            X86_64_APP_INPUT="$(make_absolute "$2")"
            shift 2
            ;;
        --keep-venvs)
            KEEP_VENVS=1
            shift
            ;;
        --skip-clean)
            SKIP_CLEAN=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "Unknown option: $1"
            ;;
    esac
done

require_command /usr/bin/arch
require_command iconutil
require_command lipo
require_command pkgbuild
require_command productbuild
require_command sips

command -v "$PYTHON_BIN" >/dev/null 2>&1 || die "Python interpreter not found: $PYTHON_BIN"
[[ -f "$SPEC_PATH" ]] || die "PyInstaller spec not found: $SPEC_PATH"
[[ -n "$ARM64_PYTHON" ]] || ARM64_PYTHON="$PYTHON_BIN"
[[ -n "$X86_64_PYTHON" ]] || X86_64_PYTHON="$PYTHON_BIN"

APP_VERSION="$(read_app_version)"
FINAL_PKG_PATH="$DIST_ROOT/${APP_NAME}-macOS-universal.pkg"

if [[ -n "$ENTITLEMENTS_FILE" && ! -f "$ENTITLEMENTS_FILE" ]]; then
    die "Entitlements file not found: $ENTITLEMENTS_FILE"
fi

if [[ -n "$ARM64_APP_INPUT" && ! -d "$ARM64_APP_INPUT" ]]; then
    die "Apple Silicon app bundle not found: $ARM64_APP_INPUT"
fi

if [[ -n "$X86_64_APP_INPUT" && ! -d "$X86_64_APP_INPUT" ]]; then
    die "Intel app bundle not found: $X86_64_APP_INPUT"
fi

if [[ "$SKIP_CLEAN" -eq 0 ]]; then
    rm -rf "$DIST_APPS_ROOT" "$PKG_ROOT" "$DIST_XML_PATH" "$ICON_PATH"
    rm -f "$FINAL_PKG_PATH"
    if [[ "$KEEP_VENVS" -eq 0 ]]; then
        rm -rf "$BUILD_ROOT/venv-arm64" "$BUILD_ROOT/venv-x86_64"
    fi
fi

mkdir -p "$BUILD_ROOT" "$DIST_ROOT" "$DIST_APPS_ROOT" "$PKG_ROOT"

if [[ -z "$ARM64_APP_INPUT" && "$HOST_ARCH" != "arm64" ]]; then
    die "An Apple Silicon host or a prebuilt --arm64-app bundle is required to package the arm64 app."
fi

if [[ -z "$X86_64_APP_INPUT" && "$HOST_ARCH" == "arm64" ]]; then
    ensure_rosetta
fi

prepare_icon

ARM64_APP_PATH="$ARM64_APP_INPUT"
X86_64_APP_PATH="$X86_64_APP_INPUT"

if [[ -z "$ARM64_APP_PATH" ]]; then
    ARM64_APP_PATH="$(build_app_for_arch arm64 "$ARM64_PYTHON" "$BUILD_ROOT/venv-arm64")"
else
    log "Using prebuilt Apple Silicon app bundle at $ARM64_APP_PATH"
    verify_app_bundle_arch "$ARM64_APP_PATH" "arm64"
fi

if [[ -z "$X86_64_APP_PATH" ]]; then
    X86_64_APP_PATH="$(build_app_for_arch x86_64 "$X86_64_PYTHON" "$BUILD_ROOT/venv-x86_64")"
else
    log "Using prebuilt Intel app bundle at $X86_64_APP_PATH"
    verify_app_bundle_arch "$X86_64_APP_PATH" "x86_64"
fi

ARM64_COMPONENT_PKG="$(package_app_bundle "$ARM64_APP_PATH" "arm64")"
X86_64_COMPONENT_PKG="$(package_app_bundle "$X86_64_APP_PATH" "x86_64")"

write_distribution_xml "$(basename "$ARM64_COMPONENT_PKG")" "$(basename "$X86_64_COMPONENT_PKG")"
build_installer_product "$FINAL_PKG_PATH"

log "Universal installer created:"
log "  $FINAL_PKG_PATH"
log "App bundles:"
log "  $ARM64_APP_PATH"
log "  $X86_64_APP_PATH"
