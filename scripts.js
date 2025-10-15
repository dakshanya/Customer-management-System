function goToSignup() {
    window.location.href = "/register"; // Ensure this page exists
  }

  // Password validation
  document.getElementById("loginForm").addEventListener("submit", function (e) {
    const passwordInput = document.getElementById("password");
    const password = passwordInput.value;
    const specialCharRegex = /[!@#$%^&*(),.?":{}|<>]/;

    // if (password.length < 6 || !specialCharRegex.test(password)) {
    //   e.preventDefault();
    //   alert("Password must be at least 6 characters long and contain at least one special character.");
    // }
  });// Function to navigate to Create Account page


// Function to navigate to Dashboard page after password validation
function goToDashboard() {
  const passwordInput = document.getElementById("password");
  const password = passwordInput.value;

  const specialCharRegex = /[!@#$%^&*(),.?":{}|<>]/;

  if (password.length < 6 || !specialCharRegex.test(password)) {
    alert("Password must be at least 6 characters long and contain at least one special character.");
    return;
  }

  // Navigate to dashboard page
  window.location.href = "/dashboard"; // Update path if needed
}


// Handle Create Account form submission
document.getElementById("createAccountForm").addEventListener("submit", function (e) {
  e.preventDefault(); // Prevent default form behavior

  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirmPassword");
  const passwordError = document.getElementById("passwordError");
  const confirmPasswordError = document.getElementById("confirmPasswordError");

  const passwordVal = password.value.trim();
  const confirmPasswordVal = confirmPassword.value.trim();

  // Reset previous styles and error messages
  password.classList.remove("valid", "invalid");
  confirmPassword.classList.remove("valid", "invalid");
  passwordError.textContent = "";
  confirmPasswordError.textContent = "";

  let valid = true;

  // Password validation
  const specialCharRegex = /[!@#$%^&*(),.?":{}|<>]/;
  if (passwordVal.length < 8) {
    passwordError.textContent = "Password must be at least 8 characters.";
    password.classList.add("invalid");
    valid = false;
  } else if (!specialCharRegex.test(passwordVal)) {
    passwordError.textContent = "Password must contain a special character.";
    password.classList.add("invalid");
    valid = false;
  } else {
    password.classList.add("valid");
  }

  // Confirm password validation
  if (passwordVal !== confirmPasswordVal) {
    confirmPasswordError.textContent = "Passwords do not match.";
    confirmPassword.classList.add("invalid");
    valid = false;
  } else {
    confirmPassword.classList.add("valid");
  }

  // Navigate to dashboard if all inputs are valid
  if (valid) {
    window.location.href = ""; // Adjust path if needed
  }
});

// Handle "Sign in here" link click
function goToSignin() {
  window.location.href = "/signin"; // Adjust path to your Signin page
}

