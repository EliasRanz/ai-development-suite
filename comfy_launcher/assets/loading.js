window.fadeOutLoading = function() {
  const loader = document.getElementById("loader-wrapper");
  if (loader) {
    loader.classList.add("fade-out");
  }
};

window.updateStatus = function(message) {
  const statusEl = document.getElementById('status-message');
  if (statusEl) {
    statusEl.textContent = message;
  }
};

// Listen for the F12 key to toggle developer tools (keep this)
document.addEventListener('keydown', function(event) {
    if (event.key === 'F12' || event.keyCode === 123) {
        event.preventDefault();
        if (typeof window.py_toggle_devtools === 'function') {
            window.py_toggle_devtools();
        } else if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.py_toggle_devtools === 'function') {
            window.pywebview.api.py_toggle_devtools();
        } else {
            console.warn('Python function "py_toggle_devtools" not found.');
        }
    }
});