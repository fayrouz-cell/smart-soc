document.addEventListener('DOMContentLoaded', function () {
    if (!window.__SPA_SHELL__) {
        return;
    }

    const frames = Array.from(document.querySelectorAll('.spa-frame'));
    const frameMap = {};
    frames.forEach(frame => {
        const view = frame.dataset.view;
        if (view) {
            frameMap[view] = frame;
        }
    });

    const navLinks = Array.from(document.querySelectorAll('.navbar .nav-link[data-view]'));

    function loadFrame(frame) {
        if (!frame) return;
        if (!frame.dataset.loaded) {
            frame.src = frame.dataset.src;
            frame.dataset.loaded = 'true';
        }
    }

    function setActiveNav(view) {
        navLinks.forEach(link => {
            if (link.dataset.view === view) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    function showView(view) {
        if (!frameMap[view]) {
            view = 'dashboard';
        }

        Object.entries(frameMap).forEach(([key, frame]) => {
            if (key === view) {
                frame.classList.add('active');
                loadFrame(frame);
            } else {
                frame.classList.remove('active');
            }
        });

        setActiveNav(view);
        if (location.hash !== `#${view}`) {
            history.replaceState(null, '', `#${view}`);
        }
    }

    navLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            if (!window.__SPA_SHELL__) return;
            event.preventDefault();
            const view = this.dataset.view;
            showView(view);
        });
    });

    const initialView = location.hash ? location.hash.replace('#', '') : 'dashboard';
    showView(initialView);
});

