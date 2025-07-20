// kleine Fokus-Animation
document.querySelectorAll('.register-card input').forEach(input => {
  input.addEventListener('focus', () => {
    input.style.borderColor = '#0c3a66';
  });
  input.addEventListener('blur', () => {
    input.style.borderColor = '#ccd';
  });
});
console.log("Register styles & scripts active");


