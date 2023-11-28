var updateBtns = document.getElementsByClassName('update-cart')

for(var i = 0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        var productID = this.dataset.product;
        var action = this.dataset.action;
        var quantity = this.dataset.quantity
        console.log('productID: ', productID, 'action: ', action, 'quantity: ', quantity);

        if(user === "AnonymousUser"){
            addCookieItem(productID, action, quantity)
        }else{
            updateUserOrder(productID,action, quantity)
        }
    })
}

function addCookieItem(productID, action, quantity){
//    console.log('not logged in: ')
//    console.log(productID)
    quantity = parseInt(quantity)
    if (action == 'add'){
        if (productID in cart){
            cart[productID]['quantity'] += quantity
        }else{
            cart[productID] = {'quantity':quantity}
        }
    }else if (action == 'remove'){
		cart[productID]['quantity'] -= quantity

		if (cart[productID]['quantity'] <= 0){
			console.log('Item should be deleted')
			delete cart[productID];
		}
	}
	console.log('CART:', cart)
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"

	location.reload()
}
function updateUserOrder(productID, action, quantity){
//    console.log('sending data');

    var url = '/update_item/'

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken': csrftoken
        },
        body:JSON.stringify({
            'productID': productID,
            'action': action,
            'quantity': quantity
        })
    })

    .then((response)=>{
        return response.json()
    })

    .then((data) => {
//        console.log('data:', data)
        location.reload()
    })
}