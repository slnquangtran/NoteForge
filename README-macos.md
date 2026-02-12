# NoteForge macOS Installation Guide

> **⚠️ DEPRECATED:** This file has been replaced by the comprehensive **[MAC_INSTALLATION.md](MAC_INSTALLATION.md)** guide.
> 
> Please use **[MAC_INSTALLATION.md](MAC_INSTALLATION.md)** for detailed installation instructions, troubleshooting, and best practices.

## Quick Install (Recommended)

1. **Run the pre-flight check:**
   ```bash
   python check-macos-deps.py
   ```

2. **Run the automated installation script:**
   ```bash
   chmod +x install-macos.sh
   ./install-macos.sh
   ```

3. **Run NoteForge:**
   ```bash
   source venv/bin/activate
   python3 main.py
   ```

## What's New in the Comprehensive Guide

The new **[MAC_INSTALLATION.md](MAC_INSTALLATION.md)** includes:

- ✅ Pre-flight system check script
- ✅ Python 3.12 compatibility
- ✅ Detailed troubleshooting section
- ✅ Architecture-specific instructions (Intel vs Apple Silicon)
- ✅ Performance optimization tips
- ✅ Known limitations and workarounds
- ✅ Version compatibility matrix

## Common Issues & Solutions

### Issue: "webrtcvad-wheels" installation fails
**Solution:** The script automatically falls back to the standard webrtcvad package or continues without it.

### Issue: PyTorch Metal/MPS backend problems
**Solution:** The script installs PyTorch with CPU backend which is more stable across Mac architectures.

### Issue: Permission denied errors
**Solution:** Make sure to run the installation script with proper permissions:
```bash
chmod +x install-macos.sh
```

### Issue: Microphone not working
**Solution:** Grant microphone permissions in System Preferences > Security & Privacy > Privacy

## Getting Help

- **Comprehensive Guide:** [MAC_INSTALLATION.md](MAC_INSTALLATION.md)
- **Quick Troubleshooting:** See [MAC_INSTALLATION.md#troubleshooting](MAC_INSTALLATION.md#troubleshooting)
- **GitHub Issues:** Report problems at our GitHub repository

## Architecture Specific Notes

### Apple Silicon (M1/M2/M3)
- Uses CPU-optimized PyTorch for better compatibility
- All wheels are compiled for ARM64 architecture
- Better performance with native ARM64 packages
- Python 3.12 recommended for best performance

### Intel Macs
- Standard x86_64 packages
- Full PyTorch CPU support
- Python 3.10+ supported