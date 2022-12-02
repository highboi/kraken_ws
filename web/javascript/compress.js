//make a random array
function randomArray(length) {
	var arr = [];

	for (var i=0; i < length; i++) {
		var random = Math.round(Math.random() * 1000);
		arr.push(random);
	}

	return arr;
}


/*
//a function to compress an array
async function compressArr(array) {
	var blob = new Blob(array);

	var stream = new CompressionStream("gzip");

	var newdata = blob.stream().pipeThrough(stream);

	return await new Response(newdata).blob();
}

//a function to decompress an array
async function decompressArr(array) {
	var blob = new Blob(array);

	var stream = new DecompressionStream("gzip");

	var newdata = blob.stream().pipeThrough(stream);

	return await new Response(newdata).blob();
}
*/

function hash(data) {
	return ( (0x0000FFFF & data)<<16 ) + ( (0xFFFF0000 & data)>>16 );
}

//a basic compression algorithm
function chopper() {
	//generate a random array to test compression
	var randomarr = randomArray(1000);
	console.log(randomarr);

	document.body.innerHTML += JSON.stringify(randomarr) + "<br>";

	var string = "";

	for (var i=0; i < randomarr.length; i++) {
		string += JSON.stringify(randomarr[i]);
	}

	document.body.innerHTML += string + "<br>";

	/*
	//chop the array into chunks
	for (var i=randomarr.length; i > 0; i--) {
		//get the amount of chunks of i size
		var looptimes = (randomarr.length+1)-i;

		//store chunks for this level
		var chunks = [];

		//find chunks of the array
		for (var j=0; j < looptimes; j++) {
			var chunk = randomarr.slice(i, j+i);
			chunks.push(chunk);
		}

		//analyze chunks for patterns
		for (var chunk of chunks) {
			console.log(chunk);
		}
	}
	*/
}

chopper();
