(function () {
  const progressBar = document.getElementById("todoProgressBar");
  if (!progressBar) return;

  const progress = parseInt(progressBar.dataset.progress || "0", 10);
  const totalTasks = parseInt(progressBar.dataset.total || "0", 10);

  if (Number.isNaN(progress) || Number.isNaN(totalTasks)) return;

  if (progress === 100 && totalTasks > 0) {
    triggerConfetti();
  }

  function triggerConfetti() {
    if (window.todoConfettiFired) return;

    window.todoConfettiFired = true;

    const duration = 2000;
    const end = Date.now() + duration;

    (function frame() {
      confetti({
        particleCount: 5,
        spread: 70,
        origin: { x: Math.random(), y: Math.random() - 0.2 }
      });

      if (Date.now() < end) {
        requestAnimationFrame(frame);
      }
    })();
  }
})();
