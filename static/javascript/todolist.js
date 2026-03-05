/* jshint esversion: 11 */
(function () {
  const progressBar = document.getElementById("todoProgressBar");
  const openSaveListModalButton = document.getElementById("openSaveListModal");
  const saveListModalElement = document.getElementById("saveListModal");
  const closeSaveListModalButton = document.getElementById("closeSaveListModal");
  const cancelSaveListModalButton = document.getElementById("cancelSaveListModal");

  let fallbackBackdrop = null;

  function openFallbackModal() {
    if (!saveListModalElement) return;
    saveListModalElement.style.display = "block";
    saveListModalElement.classList.add("show");
    saveListModalElement.setAttribute("aria-hidden", "false");
    saveListModalElement.setAttribute("aria-modal", "true");
    document.body.classList.add("modal-open");

    fallbackBackdrop = document.createElement("div");
    fallbackBackdrop.className = "modal-backdrop fade show";
    document.body.appendChild(fallbackBackdrop);
  }

  function closeFallbackModal() {
    if (!saveListModalElement) return;
    saveListModalElement.classList.remove("show");
    saveListModalElement.style.display = "none";
    saveListModalElement.setAttribute("aria-hidden", "true");
    saveListModalElement.removeAttribute("aria-modal");
    document.body.classList.remove("modal-open");

    if (fallbackBackdrop) {
      fallbackBackdrop.remove();
      fallbackBackdrop = null;
    }
  }

  if (openSaveListModalButton && saveListModalElement) {
    openSaveListModalButton.addEventListener("click", (event) => {
      event.preventDefault();

      if (window.bootstrap?.Modal) {
        const saveListModal = window.bootstrap.Modal.getOrCreateInstance(saveListModalElement);
        saveListModal.show();
        return;
      }

      openFallbackModal();
    });

    if (closeSaveListModalButton) {
      closeSaveListModalButton.addEventListener("click", () => {
        if (!window.bootstrap?.Modal) {
          closeFallbackModal();
        }
      });
    }

    if (cancelSaveListModalButton) {
      cancelSaveListModalButton.addEventListener("click", () => {
        if (!window.bootstrap?.Modal) {
          closeFallbackModal();
        }
      });
    }

    saveListModalElement.addEventListener("click", (event) => {
      if (!window.bootstrap?.Modal && event.target === saveListModalElement) {
        closeFallbackModal();
      }
    });

    document.addEventListener("keydown", (event) => {
      if (!window.bootstrap?.Modal && event.key === "Escape") {
        closeFallbackModal();
      }
    });
  }

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
