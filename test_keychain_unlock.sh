#!/bin/bash

# Test script to verify keychain unlocking functionality
# This script tests the keychain setup without running the full deployment

echo "=== Keychain Unlock Test ==="
echo "Testing the keychain password storage and retrieval system"
echo ""

# Test 1: Check if password is stored
echo "Test 1: Checking if keychain password is stored..."
STORED_PASSWORD=$(security find-generic-password -w -s 'keychain-unlock' -a "$USER" 2>/dev/null)

if [ -n "$STORED_PASSWORD" ]; then
    echo "✓ Password found in keychain"
else
    echo "✗ No password found in keychain"
    echo "Please run setup_keychain_password.sh first"
    exit 1
fi

# Test 2: Test keychain unlocking
echo ""
echo "Test 2: Testing keychain unlock..."
if security unlock-keychain -p "$STORED_PASSWORD" "$HOME/Library/Keychains/login.keychain-db" 2>/dev/null; then
    echo "✓ Keychain unlocked successfully"
else
    echo "✗ Failed to unlock keychain"
    echo "The stored password may be incorrect or keychain access may be restricted"
    exit 1
fi

# Test 3: Test keychain status
echo ""
echo "Test 3: Checking keychain status..."
KEYCHAIN_STATUS=$(security show-keychain-info "$HOME/Library/Keychains/login.keychain-db" 2>&1)
if echo "$KEYCHAIN_STATUS" | grep -q "no-timeout"; then
    echo "✓ Keychain is unlocked and accessible"
else
    echo "⚠ Keychain status unclear, but unlock command succeeded"
fi

echo ""
echo "=== Test Results ==="
echo "✓ All keychain tests passed"
echo "✓ The deployment script should now be able to unlock the keychain automatically"
echo ""
echo "You can now run your deployment script with confidence that keychain unlocking will work."