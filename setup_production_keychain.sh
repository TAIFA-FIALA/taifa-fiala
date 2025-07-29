#!/bin/bash

# Setup script to run on the production server to store keychain password
# This should be run directly on the production server, not via SSH

echo "=== Production Server Keychain Setup ==="
echo "This script must be run directly on the production server (not via SSH)"
echo "to properly store the keychain password for automated deployments."
echo ""

# Check if we're in an SSH session
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "⚠ WARNING: You appear to be in an SSH session."
    echo "⚠ For best results, run this script directly on the production server console."
    echo "⚠ SSH sessions may have keychain access restrictions."
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r; echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Please run this script directly on the production server."
        exit 1
    fi
fi

# Prompt for password
echo -n "Enter your macOS login password for this server: "
read -s PASSWORD
echo ""

if [ -z "$PASSWORD" ]; then
    echo "✗ No password entered. Exiting."
    exit 1
fi

# First unlock the keychain with the provided password
echo "Testing keychain unlock with provided password..."
if ! security unlock-keychain -p "$PASSWORD" "$HOME/Library/Keychains/login.keychain-db"; then
    echo "✗ Failed to unlock keychain with provided password"
    echo "Please ensure you entered the correct login password for this server"
    exit 1
fi

echo "✓ Keychain unlock successful"

# Remove any existing stored password first
echo "Removing any existing stored password..."
security delete-generic-password -s 'keychain-unlock' -a "$USER" 2>/dev/null || true

# Store the password in keychain
echo "Storing password in keychain..."
if security add-generic-password -s 'keychain-unlock' -a "$USER" -w "$PASSWORD" "$HOME/Library/Keychains/login.keychain-db"; then
    echo "✓ Password stored successfully in keychain"
    
    # Test the stored password immediately
    echo "Testing stored password retrieval..."
    TEST_PASSWORD=$(security find-generic-password -w -s 'keychain-unlock' -a "$USER" 2>/dev/null)
    if [ -n "$TEST_PASSWORD" ]; then
        echo "✓ Password retrieval test successful"
        
        # Test keychain unlocking with retrieved password
        echo "Testing keychain unlock with retrieved password..."
        if security unlock-keychain -p "$TEST_PASSWORD" "$HOME/Library/Keychains/login.keychain-db" 2>/dev/null; then
            echo "✓ Keychain unlock test successful"
            echo "✓ Production server keychain setup completed successfully"
            
            # Set reasonable keychain timeout
            echo "Setting keychain timeout to 1 hour..."
            security set-keychain-settings -t 3600 "$HOME/Library/Keychains/login.keychain-db" 2>/dev/null || true
            
        else
            echo "⚠ Keychain unlock test failed - there may be permission issues"
            echo "The password was stored but keychain unlocking may not work in SSH sessions"
        fi
    else
        echo "⚠ Password retrieval test failed"
        echo "The password was stored but cannot be retrieved automatically"
    fi
    
    echo ""
    echo "✓ Setup completed. The deployment script should now be able to unlock the keychain."
    echo ""
    echo "Manual test commands:"
    echo "  Test password retrieval: security find-generic-password -w -s 'keychain-unlock' -a $USER"
    echo "  Test keychain unlock: security unlock-keychain -p \"\$(security find-generic-password -w -s 'keychain-unlock' -a $USER)\" ~/Library/Keychains/login.keychain-db"
    
else
    echo "✗ Failed to store password in keychain"
    echo "This could be due to keychain access restrictions or macOS security settings"
    exit 1
fi