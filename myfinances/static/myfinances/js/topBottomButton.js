// Get the button
var topButton = document.getElementById("topBtn");

// When user scrolls down 600px from the top of the document, show the button
window.onscroll = function () { scrollFunction() };

function scrollFunction() {
    if (document.body.scrollTop > 600 || document.documentElement.scrollTop > 600) {
        topButton.style.display = "block";
    } else {
        topButton.style.display = "none";
    }
};

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}



// Get the button
var bottomButton = document.getElementById("bottomBtn");

function scrollFunction() {
    if (document.body.scrollTop > 600 || document.documentElement.scrollTop > 600) {
        topButton.style.display = "block";
        bottomButton.style.display = "block";
    } else {
        topButton.style.display = "none";
        bottomButton.style.display = "none";
    }
};

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}

// When the user clicks on the button, scroll to the bottom of the document
function bottomFunction() {
    window.scrollTo(0, document.body.scrollHeight);
}