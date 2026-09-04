import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── neural network (your original code) ──
X = np.array([[0,0,1],[0,1,1],[1,0,1],[1,1,1]])
y = np.array([[0,1,1,0]]).T
syn0 = 2*np.random.random((3,4)) - 1
syn1 = 2*np.random.random((4,1)) - 1

losses = []
iterations = []

for j in range(60000):
    l1 = 1/(1+np.exp(-(np.dot(X,syn0))))
    l2 = 1/(1+np.exp(-(np.dot(l1,syn1))))
    l2_delta = (y - l2)*(l2*(1-l2))
    l1_delta = l2_delta.dot(syn1.T) * (l1 * (1-l1))
    syn1 += l1.T.dot(l2_delta)
    syn0 += X.T.dot(l1_delta)

    if j % 1000 == 0:
        loss = np.mean(np.square(y - l2))
        losses.append(loss)
        iterations.append(j)

# ── final predictions ──
l1_final = 1/(1+np.exp(-(np.dot(X,syn0))))
l2_final = 1/(1+np.exp(-(np.dot(l1_final,syn1))))
predictions = l2_final.flatten()
targets = y.flatten()
labels = ['(0,0)', '(0,1)', '(1,0)', '(1,1)']

# ── plotting ──
fig = plt.figure(figsize=(14, 10))
fig.suptitle('XOR Neural Network — Training Visualization', fontsize=16, fontweight='bold')
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

# 1 — loss curve
ax1 = fig.add_subplot(gs[0, :])  # full width top
ax1.plot(iterations, losses, color='steelblue', linewidth=2)
ax1.fill_between(iterations, losses, alpha=0.1, color='steelblue')
ax1.set_title('Training Loss Over Time')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Mean Squared Error')
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.set_yscale('log')

# 2 — predictions vs targets
ax2 = fig.add_subplot(gs[1, 0])
x_pos = np.arange(len(labels))
width = 0.35
ax2.bar(x_pos - width/2, targets, width, label='Target', color='steelblue', alpha=0.8)
ax2.bar(x_pos + width/2, predictions, width, label='Predicted', color='coral', alpha=0.8)
ax2.set_title('Predictions vs Targets')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(labels)
ax2.set_ylabel('Output value')
ax2.set_ylim(0, 1.2)
ax2.legend()
ax2.grid(True, linestyle='--', alpha=0.3, axis='y')

# add value labels on bars
for i, (t, p) in enumerate(zip(targets, predictions)):
    ax2.text(i - width/2, t + 0.03, f'{t}', ha='center', fontsize=10)
    ax2.text(i + width/2, p + 0.03, f'{p:.2f}', ha='center', fontsize=10)

# 3 — error per input
ax3 = fig.add_subplot(gs[1, 1])
errors = np.abs(targets - predictions)
colors = ['green' if e < 0.1 else 'orange' if e < 0.3 else 'red' for e in errors]
bars = ax3.bar(labels, errors, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
ax3.set_title('Absolute Error Per Input')
ax3.set_ylabel('|Target - Predicted|')
ax3.set_ylim(0, 1)
ax3.grid(True, linestyle='--', alpha=0.3, axis='y')
ax3.axhline(y=0.1, color='green', linestyle='--', alpha=0.5, label='Good threshold')
ax3.legend(fontsize=9)

for bar, e in zip(bars, errors):
    ax3.text(bar.get_x() + bar.get_width()/2, e + 0.02, f'{e:.4f}', ha='center', fontsize=9)

plt.tight_layout()
plt.show()

# ── console summary ──
print("\n" + "="*45)
print(f"{'XOR Neural Network — Final Results':^45}")
print("="*45)
print(f"{'Input':<10} {'Target':>8} {'Predicted':>12} {'Correct':>10}")
print("-"*45)
for i, lbl in enumerate(labels):
    correct = "✓" if round(predictions[i]) == targets[i] else "✗"
    print(f"{lbl:<10} {int(targets[i]):>8} {predictions[i]:>12.4f} {correct:>10}")
print("-"*45)
final_loss = np.mean(np.square(targets - predictions))
accuracy = sum(round(p) == t for p, t in zip(predictions, targets)) / 4 * 100
print(f"Final loss:  {final_loss:.6f}")
print(f"Accuracy:    {accuracy:.0f}%")
print("="*45)