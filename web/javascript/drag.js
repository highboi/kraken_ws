//this is a function to toggle the display of an element to make it a draggable window object
function showElementDraggable(elementid) {
	//define an object to store mouse coordinates for the movement of the draggable element
	var dragCoords = {xDiff: 0, yDiff: 0, oldX: 0, oldY: 0};

	//get the element to make draggable
	var element = document.getElementById(elementid);

	//get the display property
	var display = window.getComputedStyle(element, null).getPropertyValue("display");

	//if the display value is "none"
	if (display == "none") {
		//set the display value to be absolute as we want this to be free from the document flow
		element.style.display = "block";
		element.style.position = "absolute";

		//set the dragging behavior for the draggable header element
		document.getElementById(elementid+"dragheader").onmousedown = dragMouseDown;
	} else { //if the display value is anything else
		//set the element's display value to "none"
		element.style.display = "none";
	}

	//the callback function for when a mouse button is pushed "down"
	function dragMouseDown(event) {
		//make sure we have the event with the right info
		event = event || window.event;
		event.preventDefault();

		//set the mouse cursor position according to the current position
		dragCoords.oldX = event.clientX;
		dragCoords.oldY = event.clientY;

		//make sure to move the element if the mouse is dragging
		document.onmousemove = elementDrag;

		//make sure to remove any dragging behavior once the mouse is released
		document.onmouseup = closeDragElement;
	}

	//the function to drag the element by changing the offset values in the style attribute
	function elementDrag(event) {
		//make sure we have the event with the right info
		event = event || window.event;
		event.preventDefault();

		//calculate the difference between the old coordinates and the current coordinates
		dragCoords.diffX = dragCoords.oldX - event.clientX;
		dragCoords.diffY = dragCoords.oldY - event.clientY;

		//get the current coordinates of the mouse
		dragCoords.oldX = event.clientX;
		dragCoords.oldY = event.clientY;

		/*
		do collision detection between the mouse and the edge of the browser window
		and set the left offset of the element according to the calculated difference
		between the old and new mouse coordinates
		*/
		if ( !(event.clientX < 0 || event.clientX > window.innerWidth) ) {
			element.style.left = (element.offsetLeft - dragCoords.diffX) + "px";
		}
		if ( !(event.clientY < 0 || event.clientY > window.innerHeight) ) {
			//move the element on the y axis based on the calculations above
			element.style.top = (element.offsetTop - dragCoords.diffY) + "px";
		}
	}

	//the function to eliminate dragging behavior of the element
	function closeDragElement() {
		document.onmouseup = null;
		document.onmousemove = null;
	}
}
