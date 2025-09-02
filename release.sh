#!/bin/bash
# Baby Care Tracker Release Script
# Usage: ./release.sh 1.1.0

set -e  # Exit on any error

if [ "$#" -ne 1 ]; then
    echo "❌ Usage: $0 <version>"
    echo "📝 Example: $0 1.1.0"
    echo "📋 Current version: $(grep -o '"version": "[^"]*"' custom_components/baby_care_tracker/manifest.json | cut -d'"' -f4)"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

echo "🍼 Baby Care Tracker Release $TAG"
echo "================================="

# Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid version format. Use semantic versioning (e.g., 1.0.0)"
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^$TAG$"; then
    echo "❌ Tag $TAG already exists!"
    exit 1
fi

echo "📝 Updating manifest.json version..."
# Update manifest.json version (works on both macOS and Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" custom_components/baby_care_tracker/manifest.json
else
    # Linux
    sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" custom_components/baby_care_tracker/manifest.json
fi

echo "✅ Updated manifest.json to version $VERSION"

# Show what changed
echo "📋 Version updated in manifest.json:"
grep '"version"' custom_components/baby_care_tracker/manifest.json

echo ""
echo "📝 Please update CHANGELOG.md manually with release notes"
echo "⏳ Press Enter when ready to continue, or Ctrl+C to abort..."
read

# Commit changes
echo "💾 Committing changes..."
git add custom_components/baby_care_tracker/manifest.json
if git diff --cached --quiet; then
    echo "⚠️  No changes to commit"
else
    git commit -m "Release $TAG: Update version to $VERSION"
fi

# Create and push tag
echo "🏷️  Creating tag $TAG..."
git tag $TAG

echo "🚀 Pushing to GitHub..."
git push origin main
git push origin $TAG

echo ""
echo "✅ Release $TAG created successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Go to: https://github.com/tsanidisDev/nursing-tracker/releases/new?tag=$TAG"
echo "2. Create GitHub release with release notes"
echo "3. Wait 30-60 minutes for HACS to detect the update"
echo ""
echo "🍼 Happy baby tracking! 👶"
