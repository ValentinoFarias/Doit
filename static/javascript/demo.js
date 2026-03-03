/**
 * Tickr - Fake Demo Mode
 * Standalone version with:
 *  - Preloaded fake tasks
 *  - Click to complete
 *  - Animated rendering
 *  - Progress bar
 *  - Confetti at 100%
 */

(function () {

  /* ===============================
     CONFIG
  =============================== */

  const TASK_CONTAINER_ID = "demoTaskList";
  const PROGRESS_BAR_ID = "demoProgressBar";

  /* ===============================
     STATE
  =============================== */

  let demoTasks = [
    { id: 1, title: "Write project plan", completed: false },
    { id: 2, title: "Design wireframe", completed: false },
    { id: 3, title: "Build task model", completed: false }
  ];

  /* ===============================
     INIT
  =============================== */

  document.addEventListener("DOMContentLoaded", () => {
    renderTasks();
  });

  /* ===============================
     RENDER TASKS
  =============================== */

  function renderTasks() {

    const container = document.getElementById(TASK_CONTAINER_ID);
    if (!container) return;

    container.innerHTML = "";

    demoTasks.forEach(task => {

      const element = createTaskElement(task);
      container.appendChild(element);

      animateEntrance(element);
    });

    updateProgressBar();
  }

  function createTaskElement(task) {

    const button = document.createElement("button");

    button.className =
      "list-group-item list-group-item-action d-flex justify-content-between align-items-center";

    button.innerHTML = `
      <span class="${task.completed ? 'text-decoration-line-through text-muted' : ''}">
        ${task.title}
      </span>
      <span class="badge bg-${task.completed ? 'success' : 'secondary'}">
        ${task.completed ? "✔ Done" : "Pending"}
      </span>
    `;

    button.onclick = () => toggleTask(task.id);

    return button;
  }

  /* ===============================
     TOGGLE TASK
  =============================== */

  function toggleTask(taskId) {

    const task = demoTasks.find(t => t.id === taskId);
    if (!task) return;

    task.completed = !task.completed;

    renderTasks();
  }

  /* ===============================
     PROGRESS BAR
  =============================== */

  function updateProgressBar() {

    const bar = document.getElementById(PROGRESS_BAR_ID);
    if (!bar) return;

    const total = demoTasks.length;
    const completed = demoTasks.filter(t => t.completed).length;
    const percent = total === 0 ? 0 : Math.round((completed / total) * 100);

    bar.style.width = percent + "%";
    bar.innerText = percent + "% Completed";

    bar.classList.remove("bg-primary", "bg-success");

    if (percent === 100 && total > 0) {
      bar.classList.add("bg-success");
      triggerConfetti();
    } else {
      bar.classList.add("bg-primary");
      window.confettiFired = false;
    }
  }

  /* ===============================
     CONFETTI
  =============================== */

  function triggerConfetti() {

    if (window.confettiFired) return;

    window.confettiFired = true;

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

  /* ===============================
     ANIMATION
  =============================== */

  function animateEntrance(element) {

    element.style.opacity = 0;
    element.style.transform = "translateY(15px)";

    setTimeout(() => {
      element.style.transition = "0.3s ease";
      element.style.opacity = 1;
      element.style.transform = "translateY(0)";
    }, 30);
  }

  /* ===============================
     OPTIONAL: Add New Fake Task
  =============================== */

  window.addFakeTask = function () {

    const nextId = demoTasks.length
      ? Math.max(...demoTasks.map(t => t.id)) + 1
      : 1;

    demoTasks.push({
      id: nextId,
      title: `New Task ${nextId}`,
      completed: false
    });

    renderTasks();
  };

})();