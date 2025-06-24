// views/static/js/script.js
document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM полностью загружен");
    
    // Отладка Swiper
    const swiperElement = document.querySelector('.mySwiper');
    if (swiperElement) {
        console.log("Элемент .mySwiper найден");
        const slides = swiperElement.querySelectorAll('.swiper-slide');
        console.log("Количество слайдов:", slides.length);
        
        // Находим кнопки навигации
        const nextButton = document.getElementById('news-next');
        const prevButton = document.getElementById('news-prev');
        
        if (nextButton && prevButton) {
            console.log("Кнопки навигации найдены");
        } else {
            console.error("Кнопки навигации не найдены");
        }
    } else {
        console.error("Элемент .mySwiper не найден!");
    }
    
    // Инициализация Swiper для новостей
    if (document.querySelector('.mySwiper')) {
        try {
            // Инициализация Swiper v8
            const swiper = new Swiper('.mySwiper', {
                slidesPerView: 1,
                spaceBetween: 30,
                centeredSlides: true, // Центрирует активный слайд
                loop: true,
                autoplay: {
                    delay: 5000,
                    disableOnInteraction: false,
                },
                effect: 'coverflow', // Добавляем эффект перекрытия
                coverflowEffect: {
                    rotate: 0,
                    stretch: 0,
                    depth: 100,
                    modifier: 1,
                    slideShadows: false,
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                navigation: {
                    nextEl: '#news-next',
                    prevEl: '#news-prev',
                },
                breakpoints: {
                    640: {
                        slidesPerView: 1.5, // Увеличиваем, чтобы было видно части соседних слайдов
                        spaceBetween: 20,
                    },
                    768: {
                        slidesPerView: 2.5, // Увеличиваем, чтобы было видно части соседних слайдов
                        spaceBetween: 30,
                    },
                    1024: {
                        slidesPerView: 3.5, // Увеличиваем, чтобы было видно части соседних слайдов
                        spaceBetween: 30,
                    },
                },
                on: {
                    init: function() {
                        console.log("Swiper инициализирован");
                        updateActiveSlide(this);
                        
                        // Добавляем активный класс кнопкам при инициализации
                        const nextButton = document.getElementById('news-next');
                        const prevButton = document.getElementById('news-prev');
                        
                        if (nextButton && prevButton) {
                            // Анимация кнопок при наведении
                            nextButton.addEventListener('mouseenter', function() {
                                this.classList.add('button-hover');
                            });
                            
                            nextButton.addEventListener('mouseleave', function() {
                                this.classList.remove('button-hover');
                            });
                            
                            prevButton.addEventListener('mouseenter', function() {
                                this.classList.add('button-hover');
                            });
                            
                            prevButton.addEventListener('mouseleave', function() {
                                this.classList.remove('button-hover');
                            });
                            
                            // Добавляем обработчики кликов, так как кнопки вынесены из слайдера
                            nextButton.addEventListener('click', function() {
                                swiper.slideNext();
                            });
                            
                            prevButton.addEventListener('click', function() {
                                swiper.slidePrev();
                            });
                        }
                    },
                    slideChange: function() {
                        console.log("Слайд изменен, активный индекс:", this.activeIndex);
                        updateActiveSlide(this);
                    }
                }
            });
            
            // Функция для обновления активного слайда
            function updateActiveSlide(swiper) {
                if (!swiper.slides) return;
                
                // Удаляем класс active у всех слайдов
                swiper.slides.forEach(slide => {
                    slide.classList.remove('swiper-slide-active-center');
                });
                
                // Добавляем класс active к активному слайду
                if (swiper.slides[swiper.activeIndex]) {
                    swiper.slides[swiper.activeIndex].classList.add('swiper-slide-active-center');
                }
            }
            
            console.log("Swiper успешно создан:", swiper);
        } catch (error) {
            console.error("Ошибка при инициализации Swiper:", error);
        }
    } else {
        console.warn("Элемент .mySwiper не найден для инициализации Swiper");
    }

    // Плавное появление меню при наведении
    document.querySelectorAll('.hover-dropdown').forEach(dropdown => {
        const menu = dropdown.querySelector('.dropdown-menu');

        if (dropdown && menu) {
            dropdown.addEventListener('mouseenter', () => {
                dropdown.classList.add('show');
                menu.classList.add('show');
            });

            dropdown.addEventListener('mouseleave', () => {
                dropdown.classList.remove('show');
                menu.classList.remove('show');
            });
        }
    });

    // Находим все выпадающие меню
    const dropdowns = document.querySelectorAll('.nav-item.dropdown');
    
    // Обрабатываем каждое выпадающее меню
    dropdowns.forEach(dropdown => {
        const dropdownToggle = dropdown.querySelector('.dropdown-toggle');
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');
        
        if (dropdownToggle && dropdownMenu) {
            let timeout;

            // Показываем меню при наведении
            dropdown.addEventListener('mouseenter', () => {
                clearTimeout(timeout);
                dropdownMenu.classList.add('show');
                dropdownToggle.setAttribute('aria-expanded', 'true');
            });

            // Скрываем меню при уходе курсора с задержкой
            dropdown.addEventListener('mouseleave', () => {
                timeout = setTimeout(() => {
                    dropdownMenu.classList.remove('show');
                    dropdownToggle.setAttribute('aria-expanded', 'false');
                }, 300); // Задержка перед закрытием
            });

            // Останавливаем таймер, если курсор вернулся на меню
            dropdownMenu.addEventListener('mouseenter', () => {
                clearTimeout(timeout);
            });

            // Запускаем таймер закрытия при уходе с меню
            dropdownMenu.addEventListener('mouseleave', () => {
                timeout = setTimeout(() => {
                    dropdownMenu.classList.remove('show');
                    dropdownToggle.setAttribute('aria-expanded', 'false');
                }, 300);
            });
            
            // Обрабатываем клик по ссылке выпадающего меню
            dropdownToggle.addEventListener('click', function(e) {
                // Если есть атрибут href и это не "#"
                if (this.getAttribute('href') && this.getAttribute('href') !== '#') {
                    // Переходим по ссылке
                    window.location.href = this.getAttribute('href');
                }
            });
        }
    });

    // === Инициализация всплывающих подсказок Bootstrap ===
    // Инициализация всплывающих подсказок
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Инициализация всплывающих окон
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Инициализация тостов
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    var toastList = toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl);
    });
    toastList.forEach(toast => toast.show());

    // Добавление активного класса для текущего пункта меню
    const currentLocation = location.pathname;
    const menuItems = document.querySelectorAll('.nav-link');
    const menuLength = menuItems.length;
    
    for (let i = 0; i < menuLength; i++) {
        if (menuItems[i].getAttribute('href') === currentLocation) {
            menuItems[i].classList.add('active');
        }
    }
});