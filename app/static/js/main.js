/**
 * VigorPulse Fitness - Public Vanilla JavaScript
 * Smooth interactions, real-time validation, AJAX form submission
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const navMenu = document.getElementById('navMenu');

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', () => {
      navMenu.classList.toggle('open');
      const isExpanded = navMenu.classList.contains('open');
      mobileToggle.setAttribute('aria-expanded', isExpanded);
    });

    // Close menu when clicking outside or clicking any nav link
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('open');
      });
    });
  }

  // 2. Smooth Scroll for all internal hash links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId && targetId !== '#') {
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          e.preventDefault();
          const headerOffset = 80;
          const elementPosition = targetElement.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });
        }
      }
    });
  });

  // 3. Quick-Book from Program Cards
  document.querySelectorAll('.btn-book-program').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const programTitle = this.getAttribute('data-program');
      const goalSelect = document.getElementById('fitness_goal');
      const bookingSection = document.getElementById('booking');

      if (goalSelect && programTitle) {
        // Find matching option
        for (let i = 0; i < goalSelect.options.length; i++) {
          if (goalSelect.options[i].text.toLowerCase() === programTitle.toLowerCase()) {
            goalSelect.selectedIndex = i;
            goalSelect.classList.remove('is-invalid');
            break;
          }
        }
      }

      if (bookingSection) {
        const headerOffset = 80;
        const targetPos = bookingSection.getBoundingClientRect().top + window.pageYOffset - headerOffset;
        window.scrollTo({ top: targetPos, behavior: 'smooth' });
      }
    });
  });

  // 4. Custom Gender Radio Button Selection
  const genderLabels = document.querySelectorAll('.radio-card');
  genderLabels.forEach(label => {
    const radio = label.querySelector('input[type="radio"]');
    if (radio && radio.checked) {
      label.classList.add('active');
    }

    label.addEventListener('click', () => {
      genderLabels.forEach(l => l.classList.remove('active'));
      label.classList.add('active');
      if (radio) {
        radio.checked = true;
        clearFieldError('gender');
      }
    });
  });

  // 5. Booking Form Validation & AJAX Submission
  const bookingForm = document.getElementById('bookingForm');
  const successCard = document.getElementById('bookingSuccessAlert');

  if (bookingForm) {
    const nameInput = document.getElementById('name');
    const phoneInput = document.getElementById('phone');
    const emailInput = document.getElementById('email');
    const goalSelect = document.getElementById('fitness_goal');
    const typeSelect = document.getElementById('training_type');

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

    // Submit handler with AJAX & fallback
    bookingForm.addEventListener('submit', async (e) => {
      e.preventDefault();

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

        const data = await response.json();

        if (response.ok && data.success) {
          bookingForm.reset();
          genderLabels.forEach(l => l.classList.remove('active'));

          if (successCard) {
            successCard.style.display = 'block';
            successCard.innerHTML = `
              <div style="font-size: 2rem; margin-bottom: 8px;">🎉</div>
              <h3 style="color:#10b981; margin-bottom: 6px;">Free Trial Booked!</h3>
              <p>${data.message || "Thank you! We will contact you within 24 hours."}</p>
            `;
            successCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        } else {
          if (data.errors) {
            for (const [key, errorList] of Object.entries(data.errors)) {
              showFieldError(key, errorList[0]);
            }
          } else if (data.message) {
            alert(data.message);
          }
        }
      } catch (err) {
        console.error("Booking error:", err);
        // Fallback to regular form submission if fetch failed
        bookingForm.submit();
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
