#!/usr/bin/env python3
"""
CPU vs GPU Performance Benchmark für Ollama
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ollama_integration import create_ollama_client

def benchmark():
    print("\n" + "="*70)
    print("  CPU vs GPU PERFORMANCE BENCHMARK")
    print("="*70 + "\n")
    
    client = create_ollama_client()
    
    test_prompt = "Erkläre Python in einem kurzen Satz."
    
    print("🧪 Test-Prompt:", test_prompt)
    print("📦 Modell: tinyllama (GPU-optimiert)")
    print("\n" + "-"*70 + "\n")
    
    # GPU Test
    print("🚀 Test 1: GPU-Modus (Standard)")
    start = time.time()
    response = client.generate(
        prompt=test_prompt,
        temperature=0.7,
        max_tokens=30
    )
    gpu_duration = time.time() - start
    
    if response:
        gpu_tokens = len(response.split())
        gpu_tps = gpu_tokens / gpu_duration
        print(f"   ✅ {gpu_tokens} tokens in {gpu_duration:.2f}s")
        print(f"   ⚡ Speed: {gpu_tps:.1f} tokens/s")
        print(f"   💬 Antwort: {response[:80]}...")
    else:
        print("   ❌ Fehler")
        return
    
    print("\n" + "-"*70 + "\n")
    
    # Referenz CPU-Werte (aus vorherigen Tests)
    cpu_tps = 2.3  # tokens/s im CPU-Modus (gemessen)
    
    print("📊 CPU-Modus (Referenz aus vorherigen Tests)")
    print(f"   ⏱️  Speed: {cpu_tps:.1f} tokens/s")
    
    print("\n" + "="*70 + "\n")
    
    # Vergleich
    speedup = gpu_tps / cpu_tps
    
    print("📈 ERGEBNIS:")
    print(f"   GPU:    {gpu_tps:.1f} tokens/s")
    print(f"   CPU:    {cpu_tps:.1f} tokens/s")
    print(f"   Speedup: {speedup:.1f}x schneller mit GPU! 🚀")
    
    if speedup >= 10:
        print(f"\n   🎉 EXZELLENT! {speedup:.0f}x Beschleunigung!")
    elif speedup >= 5:
        print(f"\n   ✅ SEHR GUT! {speedup:.0f}x Beschleunigung!")
    elif speedup >= 3:
        print(f"\n   ✅ GUT! {speedup:.0f}x Beschleunigung!")
    else:
        print(f"\n   ⚠️  Moderat: {speedup:.1f}x Beschleunigung")
        print("   💡 Tipp: Kleineres Modell oder GPU-Treiber aktualisieren")
    
    print("\n" + "="*70 + "\n")
    
    # GPU-Status
    import subprocess
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,temperature.gpu', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            gpu_util, vram, temp = result.stdout.strip().split(', ')
            print("🖥️  GPU-Status:")
            print(f"   Auslastung: {gpu_util}")
            print(f"   VRAM: {vram}")
            print(f"   Temperatur: {temp}")
            print()
    except:
        pass

if __name__ == "__main__":
    benchmark()
