document.querySelectorAll(".toggle-password").forEach(function (eyeIcon) {
        eyeIcon.addEventListener("click", function () {
            const input = document.querySelector(this.getAttribute("toggle"));
            const type = input.getAttribute("type") === "password" ? "text" : "password";
            input.setAttribute("type", type);
            this.classList.toggle("bi-eye");
            this.classList.toggle("bi-eye-slash");
        });
});

window.addEventListener('scroll', function () {
        const header = document.querySelector('.Header_section');
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
});
