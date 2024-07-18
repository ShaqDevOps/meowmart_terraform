function updatePrimaryImage(thumbnail) {
    var primaryImage = document.getElementById('primary-image');
    primaryImage.src = thumbnail.src;
    var thumbnails = document.getElementsByClassName('thumbnail-image');
    for (var i = 0; i < thumbnails.length; i++) {
        thumbnails[i].classList.remove('active-thumbnail');
    }
    thumbnail.classList.add('active-thumbnail');
}

function changeQuantity(change) {
    var quantityInput = document.getElementById('quantity-input');
    var currentQuantity = parseInt(quantityInput.value, 10);
    currentQuantity += change;
    quantityInput.value = Math.max(currentQuantity, 1); // Prevent negative numbers
}