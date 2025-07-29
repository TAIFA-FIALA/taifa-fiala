#!/bin/bash

# Setup script to store keychain password for automated Docker deployments
# Run this ONCE on the production server

echo "=== Keychain Password Setup for Docker Deployments ==="
echo "This script will store your login password securely in the keychain"
echo "for automated Docker deployments over SSH."
echo ""

# Prompt for password
echo -n "Enter your macOS login password: "
read -s PASSWORD
echo ""

# First unlock the keychain with the provided password
echo "Unlocking keychain first..."
if ! security unlock-keychain -p "$PASSWORD" "$HOME/Library/Keychains/login.keychain-db"; then
    echo "✗ Failed to unlock keychain with provided password"
    echo "Please ensure you entered the correct login password"
    exit 1
fi

# Remove any existing stored password first
echo "Removing any existing stored password..."
security delete-generic-password -s 'keychain-unlock' -a "$USER" 2>/dev/null || true

# Store the password in keychain without trusted applications (more compatible)
echo "Storing password in keychain..."
security add-generic-password -s 'keychain-unlock' -a "$USER" -w "$PASSWORD" "$HOME/Library/Keychains/login.keychain-db"

if [ $? -eq 0 ]; then
    echo "✓ Password stored successfully in keychain"
    echo "✓ The deployment script can now unlock the keychain automatically"
    echo ""
    
    # Test the stored password immediately
    echo "Testing stored password retrieval..."
    TEST_PASSWORD=$(security find-generic-password -w -s 'keychain-unlock' -a "$USER" 2>/dev/null)
    if [ -n "$TEST_PASSWORD" ]; then
        echo "✓ Password retrieval test successful"
        
        # Test keychain unlocking with retrieved password
        echo "Testing keychain unlock with retrieved password..."
        if security unlock-keychain -p "$TEST_PASSWORD" "$HOME/Library/Keychains/login.keychain-db" 2>/dev/null; then
            echo "✓ Keychain unlock test successful"
            echo "✓ Setup completed successfully - deployment script should now work"
        else
            echo "⚠ Keychain unlock test failed - there may be permission issues"
            echo "You may need to run this setup again or check keychain permissions"
        fi
    else
        echo "⚠ Password retrieval test failed"
        echo "The password was stored but cannot be retrieved automatically"
        echo "This may indicate a keychain access issue"
    fi
    
    echo ""
    echo "Manual test commands:"
    echo "  Test password retrieval: security find-generic-password -w -s 'keychain-unlock' -a $USER"
    echo "  Test keychain unlock: security unlock-keychain -p \"\$(security find-generic-password -w -s 'keychain-unlock' -a $USER)\" ~/Library/Keychains/login.keychain-db"
    echo ""
    echo "To remove the stored password later:"
    echo "  security delete-generic-password -s 'keychain-unlock' -a $USER"
else
    echo "✗ Failed to store password in keychain"
    echo "This could be due to:"
    echo "  - Incorrect password"
    echo "  - Keychain access restrictions"
    echo "  - macOS security settings"
    echo ""
    echo "Try running this script again or check your keychain settings in System Preferences"
    exit 1
fi
