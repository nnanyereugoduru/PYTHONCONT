
ax1.plot(iterations, losses, color='steelblue', linewidth=2)
ax1.fill_between(iterations, losses, alpha=0.1, color='steelblue')
ax1.set_title('Training Loss Over Time')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Mean Squared Error')
ax1.grid(True, linestyle='--', alpha=0.5)