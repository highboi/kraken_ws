//get all of the pages in the dashboard
var pages = document.querySelectorAll("#panel .page");

//show the network dashboard
document.querySelector("#banner-bottom #kraken-network").addEventListener("click", (event) => {
	for (var page of pages) {
		page.style.display = "none";
	}

	document.querySelector("#panel #network").style.display = "inherit";
});

//show the code upload and web assembly compiler
document.querySelector("#banner-bottom #wasm-compile").addEventListener("click", (event) => {
	for (var page of pages) {
		page.style.display = "none";
	}

	document.querySelector("#panel #wasm-upload").style.display = "inherit";
});

//show the current binaries on the network
document.querySelector("#banner-bottom #wasm-manage").addEventListener("click", (event) => {
	for (var page of pages) {
		page.style.display = "none";
	}

	document.querySelector("#panel #wasm").style.display = "inherit";
});
