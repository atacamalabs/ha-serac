# Quick Start Guide

## 🎉 Phase 1 is Complete!

Your Home Assistant HACS integration is ready for GitHub and beta testing.

## What You Have Now

✅ **v0.1.0b1** - Full AROME weather integration
- Weather entity with forecasts
- 11 weather sensors
- HACS-ready structure
- Complete documentation
- Git repository initialized

## Immediate Next Steps

### 1. Update Your GitHub Username (Required)

Replace `yourusername` in these files with your actual GitHub username:

```bash
# Option A: Using sed (macOS/Linux)
sed -i '' 's/yourusername/YOUR_GITHUB_USERNAME/g' README.md
sed -i '' 's/yourusername/YOUR_GITHUB_USERNAME/g' custom_components/better_mountain_weather/manifest.json

# Option B: Manually edit the files
# - Open README.md and find/replace "yourusername"
# - Open custom_components/better_mountain_weather/manifest.json and do the same
```

Commit the changes:
```bash
git add README.md custom_components/better_mountain_weather/manifest.json
git commit -m "Update GitHub username in documentation"
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ha-better-mountain-weather`
3. Make it **Public**
4. **Don't** initialize with README
5. Click "Create repository"

### 3. Push Your Code

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/ha-better-mountain-weather.git

# Push code and tags
git push -u origin main
git push origin v0.1.0b1
```

### 4. Create GitHub Release

1. Go to your repository on GitHub
2. Click "Releases" → "Draft a new release"
3. Click "Choose a tag" → Select `v0.1.0b1`
4. Title: `v0.1.0b1 - Beta 1: AROME Weather Integration`
5. Check ✅ "Set as a pre-release"
6. Copy this description:

```markdown
## 🏔️ First Beta Release - AROME Weather Forecasts

Complete weather forecasts for French Alps, Pyrenees, and Corsica!

### Features
- Weather entity with current conditions
- 7-day daily + 48-hour hourly forecasts
- 11 comprehensive AROME sensors
- GPS coordinate-based setup

### Installation
1. Add this repo to HACS as custom repository
2. Install "A Better Mountain Weather"
3. Restart Home Assistant
4. Configure with your API tokens

### Requirements
- AROME API token from https://portail-api.meteofrance.fr/
- BRA API token (same portal)

**This is a beta release - feedback welcome!**
```

7. Click "Publish release"

### 5. Test Installation

1. Open Home Assistant
2. Go to HACS → Integrations
3. Click ⋮ → Custom repositories
4. Add: `https://github.com/YOUR_USERNAME/ha-better-mountain-weather`
5. Category: Integration
6. Click "Add"
7. Find "A Better Mountain Weather" and install
8. Restart Home Assistant
9. Add integration via Settings → Devices & Services

## Getting API Tokens

You'll need both tokens to test:

### AROME Token
1. Visit https://portail-api.meteofrance.fr/
2. Create account
3. Subscribe to AROME API
4. Copy your API key

### BRA Token
1. Same portal
2. Subscribe to BRA API
3. Copy your API key

## Test Configuration

Use these test coordinates:

- **Chamonix**: 45.9237, 6.8694
- **Grenoble**: 45.1885, 5.7245
- **Val d'Isère**: 45.4486, 6.9808

## Troubleshooting

### "Invalid API token"
- Check you copied the token correctly
- Verify subscription is active

### "Cannot connect"
- Check GPS coordinates format
- Verify internet connection
- Ensure coordinates are in France

### Integration doesn't appear
- Restart Home Assistant completely
- Check System Logs for errors

## Share with Beta Testers

Send them:
1. Repository URL
2. Installation instructions from README
3. How to get API tokens

## What's Next?

**Phase 2** will add BRA avalanche risk sensors:
- 8 avalanche sensors
- Auto massif detection
- Manual massif override

See `DEVELOPMENT.md` for Phase 2 implementation plan.

## Support

- **Issues**: Use GitHub Issues in your repository
- **Questions**: Use GitHub Discussions

---

**Need help?** Check `DEVELOPMENT.md` for detailed guidance.
