/**
 * EMS Main JavaScript
 * Handles Theme Toggling (Dark Mode), Sidebar Offcanvas, Dynamic Modals & Tooltips
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Theme (Dark / Light Mode) Management
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const htmlElement = document.documentElement;

  function getStoredTheme() {
    return localStorage.getItem('ems_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }

  function setTheme(theme) {
    htmlElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('ems_theme', theme);
    updateThemeIcon(theme);
  }

  function updateThemeIcon(theme) {
    if (!themeToggleBtn) return;
    const icon = themeToggleBtn.querySelector('i');
    if (!icon) return;
    if (theme === 'dark') {
      icon.className = 'bi bi-sun-fill text-warning';
      themeToggleBtn.setAttribute('title', 'Switch to Light Mode');
    } else {
      icon.className = 'bi bi-moon-stars-fill text-secondary';
      themeToggleBtn.setAttribute('title', 'Switch to Dark Mode');
    }
  }

  // Initial load
  setTheme(getStoredTheme());

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
      const current = htmlElement.getAttribute('data-bs-theme') || 'light';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  // 2. Responsive Sidebar Toggle for Tablets & Mobile
  const sidebarToggleBtn = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('app-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');

  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('show');
      if (backdrop) backdrop.classList.toggle('show');
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', function () {
      sidebar.classList.remove('show');
      backdrop.classList.remove('show');
    });
  }

  // 3. Initialize Bootstrap Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (el) {
    return new bootstrap.Tooltip(el);
  });

  // 4. Dynamic Generic Confirmation Modal Binder
  const deleteModal = document.getElementById('deleteConfirmModal');
  if (deleteModal) {
    deleteModal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const deleteUrl = button.getAttribute('data-delete-url');
      const deleteName = button.getAttribute('data-delete-name') || 'this item';
      const deleteActionType = button.getAttribute('data-action-type') || 'delete';

      const modalForm = deleteModal.querySelector('#deleteModalForm');
      const modalItemName = deleteModal.querySelector('#deleteModalItemName');
      const modalSubmitBtn = deleteModal.querySelector('#deleteModalSubmitBtn');

      if (modalForm && deleteUrl) {
        modalForm.action = deleteUrl;
      }
      if (modalItemName) {
        modalItemName.textContent = deleteName;
      }
      if (modalSubmitBtn) {
        if (deleteActionType === 'deactivate') {
          modalSubmitBtn.textContent = 'Deactivate';
          modalSubmitBtn.className = 'btn btn-warning';
        } else {
          modalSubmitBtn.textContent = 'Delete Permanently';
          modalSubmitBtn.className = 'btn btn-danger';
        }
      }
    });
  }

  // 5. Auto dismiss messages after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 6000);
  });
});

