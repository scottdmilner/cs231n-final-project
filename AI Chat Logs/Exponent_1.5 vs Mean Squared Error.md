# Conversation
- conversationId: 112dbca4-2eb7-4cff-b705-16b7eb0393d7
- endpoint: claude
- title: Exponent 1.5 vs Mean Squared Error
- exportAt: 23:51:34 GMT-0700 (Pacific Daylight Time)

## Options
- presetId: null
- model: claude-4-5-sonnet
- resendFiles: true
- endpoint: claude
- endpointType: custom
- title: Exponent 1.5 vs Mean Squared Error

## History
**User**
What happens if instead of an mse for difference I use an exponent of 1.5


**Anthropic**
# Using an Exponent of 1.5 Instead of MSE

If you replace the Mean Squared Error (MSE) with an exponent of 1.5, you get what's sometimes called a **1.5-norm loss** or **power loss with p=1.5**:

```
L = mean(|predicted - actual|^1.5)
```

## Key Differences from MSE (p=2)

### 1. **Sensitivity to Outliers**
- **MSE (p=2)**: Heavily penalizes large errors (quadratic growth)
- **p=1.5**: Intermediate sensitivity - more than MAE (p=1) but less than MSE
- **Effect**: More robust to outliers than MSE, but still gives them more weight than small errors

### 2. **Gradient Behavior**

For error `e = |predicted - actual|`:

| Loss Type | Gradient Magnitude |
|-----------|-------------------|
| MAE (p=1) | Constant: 1 |
| **p=1.5** | **∝ \|e\|^0.5** |
| MSE (p=2) | Linear: ∝ \|e\| |

**Implications:**
- Gradients grow with error size, but **sublinearly** (slower than MSE)
- Near-zero errors have **larger gradients** than MSE (steeper than linear)
- Large errors have **smaller gradients** than MSE (flatter than linear)

### 3. **Non-Differentiability**

The derivative at `e=0` is:
```
d/de |e|^1.5 = 1.5 * |e|^0.5 * sign(e)
```

This is **undefined at e=0** (gradient → ∞), though in practice you can:
- Add a small epsilon: `(e² + ε)^0.75`
- Use subgradients (like MAE)

### 4. **Practical Effects**

**Training dynamics:**
- Faster correction of large errors than MAE
- Less aggressive than MSE on outliers
- May have stability issues near perfect predictions due to steep gradients

**When it might be useful:**
- You want outlier robustness but MAE is too insensitive to large errors
- Your data has heavy-tailed noise (between Gaussian and Laplacian)
- You want a middle ground between L1 and L2 regularization effects

## Comparison Table

| Property | MAE (p=1) | **p=1.5** | MSE (p=2) |
|----------|-----------|-----------|-----------|
| Outlier sensitivity | Low | Medium | High |
| Gradient at large errors | Small | Medium | Large |
| Differentiable at 0 | No | No | Yes |
| Common use | Robust regression | Rare | Standard |

Would you like to see a mathematical derivation of the gradients or examples of when this might be preferable?


