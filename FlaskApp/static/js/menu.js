const script = document.createElement('script');
script.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js";
script.onload = function() {
    $(document).ready(function() {
        const currentPath = window.location.pathname;
        $('#menu-placeholder').load('/templates/menu.html?path='+currentPath, function(response, status, xhr) {
            if (status == "error") {
                console.error("Error loading the menu:", xhr.status, xhr.statusText);
            }
        });
     });
};
document.head.appendChild(script);

