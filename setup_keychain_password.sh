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
security unlock-keychain -p "$PASSWORD" "$HOME/Library/Keychains/login.keychain-db"

# Store the password in keychain
echo "Storing password in keychain..."
security add-generic-password -s 'keychain-unlock' -a "$USER" -w "$PASSWORD" -T "/usr/bin/security" -T "/usr/local/bin/security" -T "" "$HOME/Library/Keychains/login.keychain-db"

if [ $? -eq 0 ]; then
    echo "✓ Password stored successfully in keychain"
    echo "✓ The deployment script can now unlock the keychain automatically"
    echo ""
    echo "To test the setup:"
    echo "  security find-generic-password -w -s 'keychain-unlock' -a $USER"
    echo ""
    echo "To remove the stored password later:"
    echo "  security delete-generic-password -s 'keychain-unlock' -a $USER"
else
    echo "✗ Failed to store password in keychain"
    exit 1
fi
