
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

// Function to create a new cart
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
        fetch(`/store/carts/${cart_id}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error fetching cart data');
                }
                return response.json();
            })
            .then(cartData => {
                const cartCountElement = document.getElementById('cart-count');
                const cartItemsListElement = document.getElementById('cart-items-list');

                if (cartCountElement) {
                    if (cartData.items.length > 0) {
                        cartCountElement.textContent = cartData.items.length;
                        cartCountElement.classList.remove('hidden');
                    } else {
                        cartCountElement.classList.add('hidden');
                    }
                }

                if (cartItemsListElement) {
                    cartItemsListElement.innerHTML = ''; // Clear current items
                    cartData.items.forEach(item => {
                        const li = document.createElement('li');
                        li.className = 'cart-item p-2 border-b border-gray-200 flex flex-col items-center';
                        const itemTotalPrice = item.quantity * item.product.unit_price;
                        const imageSrc = item.product.images.length > 0 ? item.product.images[0].image : 'path/to/default/image.jpg';
                        li.innerHTML = `
                            <a href="/store/products/${item.product.id}" class="flex flex-col items-center">
                                <img src="${imageSrc}" alt="${item.product.title}" class="cart-item-image h-24 w-24 object-cover rounded mb-2">
                                <div class="text-center">
                                    <span class="cart-item-quantity text-sm">Qty: ${item.quantity}</span>
                                    <span class="cart-item-price text-sm font-bold">$${itemTotalPrice.toFixed(2)}</span>
                                </div>
                            </a>
                        `;
                        cartItemsListElement.appendChild(li);
                    });

                    // Append the total to the cart dropdown
                    const totalLi = document.createElement('li');
                    totalLi.className = 'px-4 py-2 flex justify-between items-center border-t border-gray-200';
                    totalLi.innerHTML = `
                        <span>Total:</span>
                        <span class="font-bold">$${cartData.total_price.toFixed(2)}</span>
                    `;
                    cartItemsListElement.appendChild(totalLi);
                }
            })
            .catch(error => {
                console.error('Error fetching cart:', error);
            });
    } else {
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.classList.add('hidden');
        }
    }
}


// Function to add an item to the cart
function addToCart(productId, quantity) {
    let cart_id = localStorage.getItem('cart_id');
    if (!cart_id) {
        createCart().then(newCartId => {
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
        .then(response => {
            if (!response.ok) {
                throw new Error('Error adding item to cart');
            }
            return response.json();
        })
        .then(data => {
            updateCartUI(); // Update UI after adding to cart
        })
        .catch(error => console.error('Error:', error));
    }
}

// Function to toggle the cart dropdown visibility
function toggleCart() {
    const cartDropdown = document.getElementById('cart-dropdown');
    if (cartDropdown) {
        cartDropdown.classList.toggle('hidden');
        updateCartUI(); // Update the UI each time the cart is toggled
    } else {
        console.error('Cart dropdown element not found');
    }
}

// Event listener for when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    updateCartUI(); // Initial update of the cart UI when the page loads
    
    // Assign click event listener for the cart icon
    const cartButton = document.getElementById('cart-icon-button');
    if (cartButton) {
        cartButton.addEventListener('click', toggleCart);
    }
});