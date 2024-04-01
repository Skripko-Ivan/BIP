$(document).ready(function(){
    console.log("Loaded!")
    $.get( "auth/check", function( data ) {
        console.log(data);
        if (data.redirect === true) {
            window.location.replace(data.url);
        }
    });

    // Обработчик клика по кнопке создания статьи
    $('.create-article-btn').click(function() {
        // Предполагаем, что /create-article - это ваш эндпоинт, который делает редирект на страницу создания статьи
        window.location.href = '/create-article'; 
    });
});
