# HACS Release & Update Guide

## 🏷️ How to Release Updates for HACS

### **Step 1: Update Version Numbers**

Before creating a new release, update the version in these files:

#### 1. Update `manifest.json`
```json
{
  "version": "1.1.0"
}
```

#### 2. Update `CHANGELOG.md`
Add your new version at the top:
```markdown
## [1.1.0] - 2025-09-03
### Added
- New feature description
### Fixed
- Bug fix description
```

### **Step 2: Create GitHub Release**

#### Method 1: Command Line
```bash
# 1. Commit your changes
git add .
git commit -m "Release v1.1.0: Add new features and bug fixes"

# 2. Create and push tag
git tag v1.1.0
git push origin main
git push origin v1.1.0

# 3. Create GitHub release (manual step in GitHub UI)
```

#### Method 2: GitHub CLI (if installed)
```bash
# 1. Commit changes
git add .
git commit -m "Release v1.1.0: Add new features and bug fixes"
git push origin main

# 2. Create release with tag
gh release create v1.1.0 \
  --title "Baby Care Tracker v1.1.0" \
  --notes "## What's New
- Fixed entity configuration issues
- Improved button mapping
- Better error handling

## Installation
Download via HACS or manual installation."
```

### **Step 3: GitHub Release via Web Interface**

1. **Go to your GitHub repository**: https://github.com/tsanidisDev/nursing-tracker
2. **Click "Releases"** (on the right side)
3. **Click "Create a new release"**
4. **Fill in the details:**
   - **Tag version**: `v1.1.0` (must start with 'v')
   - **Release title**: `Baby Care Tracker v1.1.0`
   - **Description**: 
     ```markdown
     ## 🍼 Baby Care Tracker v1.1.0
     
     ### ✨ What's New
     - Fixed entity configuration validation issues
     - Improved button mapping with text input
     - Better handling of optional entity fields
     - Enhanced error messages and documentation
     
     ### 🐛 Bug Fixes
     - Resolved "Entity is neither valid entity ID nor UUID" error
     - Fixed empty entity field handling
     - Improved translation file validation
     
     ### 📋 Installation
     - **HACS**: Update via HACS integrations
     - **Manual**: Download source code and copy to custom_components
     
     ### 💝 For Mothers
     Perfect for tracking baby care with smart button integration!
     ```
5. **Click "Publish release"**

## 🔄 **How HACS Detects Updates**

### **HACS Update Detection Rules:**

1. **Semantic Versioning**: Use `v1.0.0`, `v1.1.0`, `v2.0.0` format
2. **GitHub Releases**: Must create actual GitHub releases (not just tags)
3. **Manifest Version**: Must match the tag version
4. **HACS Scan**: HACS checks for new releases every 30 minutes

### **Version Format Requirements:**
```bash
✅ Correct: v1.0.0, v1.1.0, v2.0.0
❌ Wrong: 1.0.0, version-1.0.0, release-1.0.0
```

## 📋 **Release Checklist**

### Before Release:
- [ ] Update `manifest.json` version
- [ ] Update `CHANGELOG.md` with new version
- [ ] Test integration locally
- [ ] Commit all changes
- [ ] Push to main branch

### Create Release:
- [ ] Create Git tag with `v` prefix (e.g., `v1.1.0`)
- [ ] Push tag to GitHub
- [ ] Create GitHub release with same tag
- [ ] Add meaningful release notes
- [ ] Publish release

### After Release:
- [ ] Wait 30-60 minutes for HACS to detect
- [ ] Check HACS shows update available
- [ ] Test update process

## 🚀 **Quick Release Script**

Create a script to automate releases:

```bash
#!/bin/bash
# release.sh - Quick release script

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.1.0"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

echo "🏷️  Creating release $TAG..."

# Update manifest.json version
sed -i "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" custom_components/baby_care_tracker/manifest.json

echo "✅ Updated manifest.json to version $VERSION"

# Commit changes
git add .
git commit -m "Release $TAG: Update version to $VERSION"

# Create and push tag
git tag $TAG
git push origin main
git push origin $TAG

echo "🚀 Released $TAG! Create GitHub release manually at:"
echo "https://github.com/tsanidisDev/nursing-tracker/releases/new?tag=$TAG"
```

Make it executable:
```bash
chmod +x release.sh
./release.sh 1.1.0
```

## 🔍 **Troubleshooting Updates**

### **HACS Not Showing Update:**

1. **Check Version Format:**
   ```bash
   git tag -l  # Should show v1.0.0, v1.1.0, etc.
   ```

2. **Verify GitHub Release:**
   - Go to GitHub → Releases
   - Ensure release is published (not draft)
   - Tag should match manifest version

3. **Force HACS Refresh:**
   - HACS → Integrations → ⋮ → Reload HACS
   - Wait 5-10 minutes

4. **Check HACS Logs:**
   ```bash
   grep -i "baby_care_tracker\|nursing-tracker" /config/home-assistant.log
   ```

### **Common Issues:**

- **No 'v' prefix**: Tags must be `v1.0.0`, not `1.0.0`
- **Draft release**: Release must be published, not draft
- **Version mismatch**: manifest.json version must match tag
- **HACS cache**: May take 30-60 minutes to detect

## 📈 **Version Strategy**

### **Semantic Versioning:**
- **Major (v2.0.0)**: Breaking changes
- **Minor (v1.1.0)**: New features, backward compatible
- **Patch (v1.0.1)**: Bug fixes only

### **Example Progression:**
```
v1.0.0 - Initial release
v1.0.1 - Bug fix: entity configuration
v1.1.0 - Feature: new sensors
v1.1.1 - Bug fix: translation error
v2.0.0 - Breaking: new config structure
```

Following this process ensures your HACS integration updates appear automatically in Home Assistant! 🏠✨
