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
    { id: 1, title: "☕ Morning coffee and team standup", completed: false },
    { id: 2, title: "📧 Reply to client emails", completed: false },
    { id: 3, title: "💻 Code review for PR #42", completed: false },
    { id: 4, title: "📝 Update project documentation", completed: false },
    { id: 5, title: "🎨 Design new landing page mockup", completed: false },
    { id: 6, title: "🚀 Deploy to production", completed: false }
  ];

  /* ===============================
     INIT
  =============================== */

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderTasks);
  } else {
    renderTasks();
  }

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
      "list-group-item list-group-item-action d-flex align-items-center gap-3 py-3";

    button.style.cursor = "pointer";

    const checkbox = task.completed 
      ? '<span class="fs-4">✅</span>' 
      : '<span class="fs-4">⬜</span>';

    button.innerHTML = `
      ${checkbox}
      <span class="flex-grow-1 text-start ${task.completed ? 'text-decoration-line-through text-muted' : ''}">
        ${task.title}
      </span>
      <span class="badge ${task.completed ? 'bg-success' : 'bg-secondary'} rounded-pill">
        ${task.completed ? "Done" : "To Do"}
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