/**
 * VigorPulse Fitness - Admin Portal JavaScript
 * Status change handling, sidebar toggle, color picker sync
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Sidebar Toggle
  const adminMobileToggle = document.getElementById('adminMobileToggle');
  const adminSidebar = document.getElementById('adminSidebar');

  if (adminMobileToggle && adminSidebar) {
    adminMobileToggle.addEventListener('click', () => {
      adminSidebar.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (!adminSidebar.contains(e.target) && !adminMobileToggle.contains(e.target)) {
        adminSidebar.classList.remove('open');
      }
    });
  }

  // 2. Filter Form Auto-submit on change
  const filterForm = document.getElementById('leadsFilterForm');
  if (filterForm) {
    const selects = filterForm.querySelectorAll('select');
    selects.forEach(sel => {
      sel.addEventListener('change', () => {
        filterForm.submit();
      });
    });
  }

  // 3. Inline Status Change
  document.querySelectorAll('.inline-status-select').forEach(select => {
    select.addEventListener('change', async function() {
      const leadId = this.getAttribute('data-lead-id');
      const newStatus = this.value;
      const statusBadge = document.getElementById(`status-badge-${leadId}`);
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

      const formData = new FormData();
      formData.append('status', newStatus);
      if (csrfToken) formData.append('csrf_token', csrfToken);

      try {
        const response = await fetch(`/admin/leads/${leadId}/status`, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        const data = await response.json();
        if (response.ok && data.success) {
          // Update status badge pill style
          if (statusBadge) {
            statusBadge.className = 'status-pill';
            const slug = newStatus.toLowerCase().replace(/\s+/g, '-');
            statusBadge.classList.add(`status-${slug}`);
            statusBadge.textContent = newStatus;
          }
        } else {
          alert(data.message || 'Error updating status');
        }
      } catch (err) {
        console.error('Failed to update lead status:', err);
      }
    });
  });

  // 4. Color Picker Syncer (in Settings)
  const colorPicker = document.getElementById('accentColorPicker');
  const colorInput = document.getElementById('accent_color');

  if (colorPicker && colorInput) {
    colorPicker.addEventListener('input', () => {
      colorInput.value = colorPicker.value.toUpperCase();
    });

    colorInput.addEventListener('input', () => {
      if (/^#[0-9A-F]{6}$/i.test(colorInput.value)) {
        colorPicker.value = colorInput.value;
      }
    });
  }

  // 5. Delete Confirmation
  document.querySelectorAll('.btn-delete-confirm').forEach(btn => {
    btn.addEventListener('click', function(e) {
      const itemName = this.getAttribute('data-name') || 'this item';
      if (!confirm(`Are you sure you want to permanently delete ${itemName}? This action cannot be undone.`)) {
        e.preventDefault();
      }
    });
  });
});
