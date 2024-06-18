document.getElementById('myForm').addEventListener('submit', (event) => {
    event.preventDefault();

    var card = document.getElementById('card');
    card.classList.remove('hide'); // Show spinner
});
