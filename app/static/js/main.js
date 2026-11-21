/**
 * VigorPulse Fitness - Public Vanilla JavaScript
 * Smooth interactions, real-time validation, AJAX form submission
 */

document.addEventListener('DOMContentLoaded', () => {
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const hoverPointer = window.matchMedia('(hover: hover) and (pointer: fine)');

  document.querySelectorAll('.card, .type-card').forEach(card => {
    let frame;
    card.addEventListener('pointermove', event => {
      if (motionPreference.matches || !hoverPointer.matches) return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const bounds = card.getBoundingClientRect();
        const x = (event.clientX - bounds.left) / bounds.width - 0.5;
        const y = (event.clientY - bounds.top) / bounds.height - 0.5;
        card.style.setProperty('--tilt-x', `${-y * 7}deg`);
        card.style.setProperty('--tilt-y', `${x * 7}deg`);
        card.style.setProperty('--light-x', `${(x + 0.5) * 100}%`);
        card.style.setProperty('--light-y', `${(y + 0.5) * 100}%`);
      });
    });
    card.addEventListener('pointerleave', () => {
      cancelAnimationFrame(frame);
      card.style.removeProperty('--tilt-x');
      card.style.removeProperty('--tilt-y');
      card.style.removeProperty('--light-x');
      card.style.removeProperty('--light-y');
    });
  });

  const mobileToggle = document.getElementById('mobileToggle');
  const navMenu = document.getElementById('navMenu');

  function setMenuOpen(open) {
    navMenu.classList.toggle('open', open);
    mobileToggle.setAttribute('aria-expanded', String(open));
  }

  mobileToggle.addEventListener('click', () => setMenuOpen(!navMenu.classList.contains('open')));
  navMenu.addEventListener('click', event => {
    if (event.target.closest('a')) setMenuOpen(false);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && navMenu.classList.contains('open')) {
      setMenuOpen(false);
      mobileToggle.focus();
    }
  });

  document.querySelectorAll('[data-booking-field]').forEach(link => {
    link.addEventListener('click', () => {
      const select = document.getElementById(link.dataset.bookingField);
      const value = link.dataset.bookingValue;
      if (select && Array.from(select.options).some(option => option.value === value)) {
        select.value = value;
        select.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  });

  // 5. Booking Form Validation & AJAX Submission
  const bookingForm = document.getElementById('bookingForm');
  const successCard = document.getElementById('booking-success')
  const bookingError = document.getElementById('bookingError');

  if (bookingForm) {
    const nameInput = document.getElementById('name');
    const phoneInput = document.getElementById('phone');
    const emailInput = document.getElementById('email');
    const goalSelect = document.getElementById('fitness_goal');
    const typeSelect = document.getElementById('training_type');
    const finderGoal = document.getElementById('finder-goal');
    const finderType = document.getElementById('finder-type');
    const summary = document.getElementById('selectionSummary');

    function updateSelection() {
      if (finderGoal) finderGoal.value = goalSelect.value;
      if (finderType) finderType.value = typeSelect.value;
      const goal = goalSelect.value || 'Goal not selected';
      const type = typeSelect.value || 'Format not selected';
      summary.textContent = `${goal} · ${type}`;
    }

    [[finderGoal, goalSelect], [finderType, typeSelect]].forEach(([finder, field]) => {
      if (!finder) return;
      finder.addEventListener('change', () => {
        field.value = finder.value;
        field.dispatchEvent(new Event('change', { bubbles: true }));
      });
      field.addEventListener('change', updateSelection);
    });
    updateSelection();

    // Validation Regexes
    const indianPhoneRegex = /^[6-9]\d{9}$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function cleanPhone(val) {
      let cleaned = val.replace(/[\s\-\+]/g, '');
      if (cleaned.startsWith('91') && cleaned.length === 12) {
        cleaned = cleaned.substring(2);
      }
      return cleaned;
    }

    function showFieldError(fieldId, message) {
      const field = document.getElementById(fieldId);
      const errorSpan = document.getElementById(`${fieldId}-error`);
      if (field) field.classList.add('is-invalid');
      if (errorSpan) errorSpan.textContent = message;
    }

    function clearFieldError(fieldId) {
      const field = document.getElementById(fieldId);
      const errorSpan = document.getElementById(`${fieldId}-error`);
      if (field) field.classList.remove('is-invalid');
      if (errorSpan) errorSpan.textContent = '';
    }

    // Live validation on blur
    if (nameInput) {
      nameInput.addEventListener('blur', () => {
        if (!nameInput.value.trim()) {
          showFieldError('name', 'Full Name is required.');
        } else if (nameInput.value.trim().length < 2) {
          showFieldError('name', 'Name must be at least 2 characters.');
        } else {
          clearFieldError('name');
        }
      });
    }

    if (phoneInput) {
      phoneInput.addEventListener('blur', () => {
        const cleaned = cleanPhone(phoneInput.value);
        if (!phoneInput.value.trim()) {
          showFieldError('phone', '10-digit mobile number is required.');
        } else if (!indianPhoneRegex.test(cleaned)) {
          showFieldError('phone', 'Please enter a valid 10-digit Indian number (starts with 6,7,8,9).');
        } else {
          clearFieldError('phone');
        }
      });
    }

    if (emailInput) {
      emailInput.addEventListener('blur', () => {
        if (!emailInput.value.trim()) {
          showFieldError('email', 'Email address is required.');
        } else if (!emailRegex.test(emailInput.value.trim())) {
          showFieldError('email', 'Please enter a valid email address.');
        } else {
          clearFieldError('email');
        }
      });
    }

    if (goalSelect) {
      goalSelect.addEventListener('change', () => {
        if (goalSelect.value) clearFieldError('fitness_goal');
      });
    }

    if (typeSelect) {
      typeSelect.addEventListener('change', () => {
        if (typeSelect.value) clearFieldError('training_type');
      });
    }

    bookingForm.querySelectorAll('input[name="gender"]').forEach(radio => {
      radio.addEventListener('change', () => clearFieldError('gender'));
    });

    function showBookingError(message) {
      bookingError.textContent = message;
      bookingError.hidden = false;
    }

    // Submit handler with AJAX
    bookingForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      bookingError.hidden = true;
      successCard.hidden = true;

      let isValid = true;

      // Validate Name
      if (!nameInput.value.trim()) {
        showFieldError('name', 'Full Name is required.');
        isValid = false;
      } else if (nameInput.value.trim().length < 2) {
        showFieldError('name', 'Name must be at least 2 characters.');
        isValid = false;
      } else {
        clearFieldError('name');
      }

      // Validate Phone
      const cleanedPhone = cleanPhone(phoneInput.value);
      if (!phoneInput.value.trim()) {
        showFieldError('phone', '10-digit mobile number is required.');
        isValid = false;
      } else if (!indianPhoneRegex.test(cleanedPhone)) {
        showFieldError('phone', 'Please enter a valid 10-digit Indian number (e.g. 9876543210).');
        isValid = false;
      } else {
        clearFieldError('phone');
      }

      // Validate Email
      if (!emailInput.value.trim()) {
        showFieldError('email', 'Email address is required.');
        isValid = false;
      } else if (!emailRegex.test(emailInput.value.trim())) {
        showFieldError('email', 'Please enter a valid email address.');
        isValid = false;
      } else {
        clearFieldError('email');
      }

      // Validate Gender
      const selectedGender = bookingForm.querySelector('input[name="gender"]:checked');
      if (!selectedGender) {
        showFieldError('gender', 'Please select your gender.');
        isValid = false;
      } else {
        clearFieldError('gender');
      }

      // Validate Fitness Goal
      if (!goalSelect.value) {
        showFieldError('fitness_goal', 'Please select a fitness goal.');
        isValid = false;
      } else {
        clearFieldError('fitness_goal');
      }

      // Validate Training Type
      if (!typeSelect.value) {
        showFieldError('training_type', 'Please select a training type.');
        isValid = false;
      } else {
        clearFieldError('training_type');
      }

      if (!isValid) {
        showBookingError('Check the highlighted fields and try again.');
        return;
      }

      const submitBtn = bookingForm.querySelector('button[type="submit"]');
      const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Claim 2 Days Free Trial';

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
          <svg style="animation: spin 1s linear infinite; width:18px; height:18px;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle style="opacity:0.25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path style="opacity:0.75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Processing Booking...
        `;
      }

      try {
        const formData = new FormData(bookingForm);

        const response = await fetch(bookingForm.action || '/book', {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        if (!response.headers.get('content-type')?.includes('application/json')) {
          showBookingError('We could not confirm your request. Refresh the page before trying again.');
          return;
        }
        const data = await response.json();

        if (response.ok && data.success) {
          bookingForm.reset();
          updateSelection();
          successCard.querySelector('p').textContent = data.message;
          successCard.hidden = false;
          successCard.focus();
        } else {
          showBookingError(data.message || 'Unable to submit your request.');
          if (data.errors) {
            for (const [key, errorList] of Object.entries(data.errors)) {
              showFieldError(key, errorList[0]);
            }
            }
        }
      } catch (err) {
        console.error("Booking error:", err);
        showBookingError('We could not confirm your request. Check your connection before trying again.');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnText;
        }
      }
    });
  }

  // 6. Auto-dismiss Flash Alerts
  document.querySelectorAll('.flash-alert').forEach(alertBox => {
    setTimeout(() => {
      alertBox.style.opacity = '0';
      setTimeout(() => alertBox.remove(), 300);
    }, 5000);
  });
});
