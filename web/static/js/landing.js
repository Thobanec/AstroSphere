const modal=document.getElementById('modal'),open=document.getElementById('demoBtn'),close=document.getElementById('close'),form=document.getElementById('form'),menu=document.querySelector('.menu'),nav=document.querySelector('.nav nav');document.getElementById('year').textContent=new Date().getFullYear();open.onclick=()=>{modal.classList.add('open');document.body.style.overflow='hidden'};close.onclick=()=>{modal.classList.remove('open');document.body.style.overflow=''};modal.addEventListener('click',e=>{if(e.target===modal){modal.classList.remove('open');document.body.style.overflow=''}});menu.onclick=()=>nav.classList.toggle('open');document.querySelectorAll('nav a').forEach(a=>a.onclick=()=>nav.classList.remove('open'));form.onsubmit=e=>{e.preventDefault();const n=new FormData(form).get('name');alert(`Thanks, ${n}! The demo request form is ready to connect to your email or CRM.`);form.reset();modal.classList.remove('open');document.body.style.overflow=''};

/* ============================================================
   ASTROSPHERE HERO PARALLAX
   Landing-page presentation only.
   ============================================================ */

(() => {
    const hero = document.querySelector(".hero");
    const visual = document.querySelector(".visual");

    if (!hero || !visual) {
        return;
    }

    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );

    if (reduceMotion.matches) {
        return;
    }

    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;

    hero.addEventListener("mousemove", (event) => {
        const rect = hero.getBoundingClientRect();

        const x =
            (event.clientX - rect.left) /
            rect.width;

        const y =
            (event.clientY - rect.top) /
            rect.height;

        targetX = (x - 0.5) * 2;
        targetY = (y - 0.5) * 2;
    });

    hero.addEventListener("mouseleave", () => {
        targetX = 0;
        targetY = 0;
    });

    function animate() {
        currentX +=
            (targetX - currentX) * 0.045;

        currentY +=
            (targetY - currentY) * 0.045;

        visual.style.marginLeft = `${currentX * 2}px`;
        visual.style.marginTop = `${currentY * 1}px`;

        const galaxy = visual.querySelector(".galaxy");
        const orbit1 = visual.querySelector(".o1");
        const orbit2 = visual.querySelector(".o2");
        const earth = visual.querySelector(".earth");
        const jupiter = visual.querySelector(".jupiter");
        const mars = visual.querySelector(".mars");

        if (galaxy) {
            galaxy.style.marginLeft =
                `${currentX * 5}px`;
            galaxy.style.marginTop =
                `${currentY * 3}px`;
        }

        if (orbit1) {
            orbit1.style.marginLeft =
                `${currentX * 8}px`;
            orbit1.style.marginTop =
                `${currentY * 5}px`;
        }

        if (orbit2) {
            orbit2.style.marginLeft =
                `${currentX * 12}px`;
            orbit2.style.marginTop =
                `${currentY * 7}px`;
        }

        if (earth) {
            earth.style.marginLeft =
                `${currentX * 14}px`;
            earth.style.marginTop =
                `${currentY * 9}px`;
        }

        if (jupiter) {
            jupiter.style.marginLeft =
                `${currentX * 18}px`;
            jupiter.style.marginTop =
                `${currentY * 11}px`;
        }

        if (mars) {
            mars.style.marginLeft =
                `${currentX * 22}px`;
            mars.style.marginTop =
                `${currentY * 13}px`;
        }

        requestAnimationFrame(animate);
    }

    animate();
})();