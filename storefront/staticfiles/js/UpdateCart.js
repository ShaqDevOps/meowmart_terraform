document.querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the normal form submission

    var form = this;
    // Assuming you have the cart ID and item ID available in your JavaScript
    var url = `/store/carts/${cart_id}/items/${itemId}/`; // Construct the URL
    var quantity = form.querySelector('[name="quantity"]').value;
    var data = { quantity: quantity };

    fetch(url, {
        method: 'PATCH', // Set the method to PATCH
        headers: {
            'X-CSRFToken': form.querySelector('[name="csrfmiddlewaretoken"]').value,
            'Content-Type': 'application/json',
            // Add other headers like authorization if needed
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        // Handle success
    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle errors
    });
});
