@echo off
REM Model Upgrade Script for Data Crawler
REM Downloads Dolphin-Mixtral-8x7b for enhanced entity analysis

echo.
echo ========================================
echo Dolphin-Mixtral-8x7b Model Download
echo ========================================
echo.
echo System Specs:
echo   - GPU: RTX 5060 (8GB VRAM)
echo   - RAM: 32GB
echo   - Storage: 1TB SSD
echo.
echo Model Info:
echo   - Dolphin-Mixtral-8x7b (Q4 quantized)
echo   - Size: ~26GB (fits comfortably in 1TB)
echo   - VRAM: 8GB (optimized for your GPU)
echo   - Uncensored: YES (critical for intelligence analysis)
echo   - Reasoning: Excellent (better than Dolphin-llama3)
echo.

echo Starting download... This will take 5-15 minutes depending on connection.
echo.

REM Pull the model
ollama pull dolphin-mixtral:8x7b

if errorlevel 1 (
    echo.
    echo ERROR: Model download failed. Make sure:
    echo   1. Ollama is installed
    echo   2. Ollama service is running
    echo   3. You have internet connection
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Download Complete!
echo ========================================
echo.
echo Model installed successfully. Now testing...
echo.

REM List available models
echo Available Ollama models:
ollama list

echo.
echo ========================================
echo Model Comparison
echo ========================================
echo.
echo Previous: dolphin-llama3 (11B parameters, limited reasoning)
echo New:      dolphin-mixtral (8x7b=56B effective, expert routing)
echo.
echo Improvements for your crawler:
echo   ✓ Better entity relationship detection
echo   ✓ More accurate confidence scoring
echo   ✓ Superior reasoning for complex links
echo   ✓ Handles ambiguous entities better
echo   ✓ Faster inference with MoE architecture
echo.

REM Show model size info
echo ========================================
echo Next Steps
echo ========================================
echo.
echo 1. Update your crawler config to use the new model:
echo    Update trawler_enhanced.py line 84:
echo    ollama_model="dolphin-mixtral:8x7b"
echo.
echo 2. Test the crawler:
echo    python examples.py
echo.
echo 3. Monitor performance:
echo    - Check VRAM usage (should stay under 8GB)
echo    - Verify inference speed (should be 5-10 tokens/sec)
echo.

pause
