document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('modeToggle');
    const currentMode = localStorage.getItem('theme') || 'light';
    setTheme(currentMode);

    toggleButton.addEventListener('click', () => {
        const newMode = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
        setTheme(newMode);
        localStorage.setItem('theme', newMode);
    });

    function setTheme(mode) {
        const body = document.body;
        const navbar = document.querySelector('.navbar');
        const alerts = document.querySelectorAll('.alert');
        const footer = document.querySelector("footer");
        const icons = footer.querySelectorAll("a");

        if (mode === 'dark') {
            body.classList.add('dark-mode');
            navbar.classList.remove('navbar-light', 'bg-light');
            navbar.classList.add('navbar-dark', 'bg-dark');
            toggleButton.textContent = '☀️';

            alerts.forEach(alert => alert.classList.add('bg-dark', 'text-white'));

            footer.classList.remove('bg-light', 'text-dark');
            footer.classList.add('bg-dark', 'text-light');
            icons.forEach(icon => {
                icon.classList.remove('text-dark');
                icon.classList.add('text-light');
            });

        } else {
            body.classList.remove('dark-mode');
            navbar.classList.remove('navbar-dark', 'bg-dark');
            navbar.classList.add('navbar-light', 'bg-light');
            toggleButton.textContent = '🌙';

            alerts.forEach(alert => alert.classList.remove('bg-dark', 'text-white'));

            footer.classList.remove('bg-dark', 'text-light');
            footer.classList.add('bg-light', 'text-dark');
            icons.forEach(icon => {
                icon.classList.remove('text-light');
                icon.classList.add('text-dark');
            });
        }
    }
});
