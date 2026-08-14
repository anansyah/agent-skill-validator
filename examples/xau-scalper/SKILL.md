---
name: xau-scalper
description: XAU/USD scalping strategy with risk management
version: 2.0.0
author: lgd
tags:
  - trading
  - xau
  - scalping
---

# XAU Scalper

Scalping strategy for XAU/USD with strict risk management.

## Risk Parameters

- Max risk per trade: 1%
- Daily stop loss: 3%
- Max open trades: 3

## Entry Conditions

1. RSI < 30 (oversold)
2. Price above VWAP
3. Volume > 1.5x average

## Exit Conditions

- TP: 25 points
- SL: 50 points
- Time-based exit: 5 minutes

## Dependencies

- pandas
- numpy
- requests

## API Configuration

```python
import os
API_KEY = os.environ.get("EXAMPLE_API_KEY")
API_SECRET = os.environ.get("EXAMPLE_API_SECRET")
```
