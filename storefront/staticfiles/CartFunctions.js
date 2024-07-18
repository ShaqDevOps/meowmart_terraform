// Assuming CartFunctions.js contains these functions

function createCart() {
    return fetch('/store/carts/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Cart created:', data);
        localStorage.setItem('cart_id', data.id); // Store in local storage to persist across sessions
        return data.id;
    })
    .catch(error => {
        console.error('Error creating cart:', error);
        throw error;
    });
}

function updateCartUI() {
    let cart_id = localStorage.getItem('cart_id');
    if (cart_id) {
        fetch(`/store/carts/${cart_id}/`) // Fetch the updated cart
        .then(response => {
            if (!response.ok) {
                throw new Error('Error fetching cart data');
            }
            return response.json();
        })
        .then(cartData => {
            // Update cart count
            const cartCountElement = document.getElementById('cart-count');
            cartCountElement.textContent = cartData.items.length; // The number of unique items

            // Update cart dropdown items
            const cartItemsListElement = document.getElementById('cart-items-list');
            cartItemsListElement.innerHTML = ''; // Clear current items
            cartData.items.forEach(item => {
                const li = document.createElement('li');
                li.className = 'cart-item';

                // Check if the product has images and use the first one, otherwise use a default image
                const imageSrc = item.product.images && item.product.images.length > 0 
                                 ? item.product.images[0].image 
                                 : 'path/to/default/image.jpg';

                li.innerHTML = `
                    <img src="${imageSrc}" alt="${item.product.title}" class="cart-item-image">
                    <span class="cart-item-title">${item.product.title}</span>
                    <span class="cart-item-quantity">Qty: ${item.quantity}</span>
                    <span class="cart-item-price">$${(item.quantity * item.product.unit_price).toFixed(2)}</span>
                `;

                cartItemsListElement.appendChild(li);
            });

            // Update total price
            const cartTotalElement = document.getElementById('cart-total');
            if (cartTotalElement) {
                cartTotalElement.textContent = `Total: $${cartData.total_price.toFixed(2)}`;
            }
        })
        .catch(error => {
            console.error('Error fetching cart:', error);
        });
    }
}



function addToCart(productId, quantity) {
    let cart_id = localStorage.getItem('cart_id');

    if (!cart_id) {
        createCart().then(newcart_id => {
            cart_id = newcart_id;
            addToCart(productId, quantity); // Recursively call addToCart with the new cart_id
        });
    } else {
        fetch(`/store/carts/${cart_id}/items/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ product_id: productId, quantity: quantity })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Added to cart:', data);
            updateCartUI(); // Update the UI after adding to cart
        })
        .catch(error => console.error('Error:', error));
    }
}

// Helper function to get the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// You would also need to implement the updateCartUI function to reflect changes in the UI.


function updateCartItem(cartItemId, quantity) {
    const cart_id = sessionStorage.getItem('cart_id');
    fetch(`/store/carts/${cart_id}/items/${cartItemId}/`, {  // Adjust the URL to match your API endpoint for updating items
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Updated cart item:', data);
        updateCartUI(data);
    })
    .catch(error => console.error('Error:', error));
}

function removeCartItem(cartItemId) {
    const cart_id = sessionStorage.getItem('cart_id');
    fetch(`/store/carts/${cart_id}/items/${cartItemId}/`, {  // Adjust the URL to match your API endpoint for removing items
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            console.log('Removed cart item');
            updateCartUI();  // Call to update UI after item removal
        }
    })
    .catch(error => console.error('Error:', error));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleCart() {
    const cartDropdown = document.getElementById('cart-dropdown');
    cartDropdown.style.display = cartDropdown.style.display === 'block' ? 'none' : 'block';
    console.log('Toggled cart dropdown visibility.');
}

document.addEventListener('DOMContentLoaded', function() {
    let cart_id = sessionStorage.getItem('cart_id');
    if (cart_id) {
        // Optionally, fetch cart details from server and update UI
        // fetch(`/store/carts/${cart_id}`).then(...)...
    }
});


/*function createCart() {
    return fetch('/store/carts/', {  // Adjust the URL to match your API endpoint
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include' // Needed to include cookies with the request
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Cart created:', data);
        // Here you can choose between localStorage or sessionStorage
        localStorage.setItem('cart_id', data.id); // Use localStorage if you want it to persist across sessions
        // sessionStorage.setItem('cart_id', data.id); // Use sessionStorage if you want it to persist only for the current session
        return data.id;
    })
    .catch(error => {
        console.error('Error creating cart:', error);
        throw error;
    });
}

function createCart() {
    return fetch('/store/carts/', {  // Adjust the URL to match your API endpoint
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include' // Needed to include cookies with the request
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Cart created:', data);
        sessionStorage.setItem('cart_id', data.id); // Saving the cart_id to sessionStorage
        return data.id;
    })
    .catch(error => {
        console.error('Error creating cart:', error);
        throw error;
    });
}

function addToCart(productId, quantity) {
    let cart_id = sessionStorage.getItem('cart_id');

    if (!cart_id) {
        createCart().then(newcart_id => {
            // Now that we have a newcart_id, add the item to the cart
            addToCart(productId, quantity, newcart_id); // Call addToCart with the new cart_id
        });
    } else {
        fetch(`/store/carts/${cart_id}/items/`, {  // Adjust the URL to match your API endpoint for adding items
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ product_id: productId, quantity: quantity })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Added to cart:', data);
            // This function should be implemented to update the cart icon/count in your UI
            updateCartUI(data); 
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

// This function updates the cart UI with the given cartData
function updateCartUI(cartData) {
    // Update the cart count display
    const cartCountElement = document.getElementById('cart-count');
    cartCountElement.textContent = cartData.items.length; // Update with the number of items in the cart

    // Update the cart items list display
    const cartItemsListElement = document.getElementById('cart-items-list');
    cartItemsListElement.innerHTML = ''; // Clear current cart items

    // Add each cart item to the list
    cartData.items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `${item.product.title} - Quantity: ${item.quantity}`;
        cartItemsListElement.appendChild(li);
    });

    // If you have some kind of subtotal or total cost display, update that here too
    const cartTotalElement = document.getElementById('cart-total');
    cartTotalElement.textContent = `Total: $${cartData.total_price.toFixed(2)}`;
}
 */